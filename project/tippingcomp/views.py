
from django.contrib.auth import authenticate, get_user
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.static import serve

from .models import Bet, Match, Team, User
from .squiggle import update, updateTeams
from .funcs import add_match_info


def index(request):
    return render(request, 'index.html')


def css(request, file):
    return serve(request, file + '.css', 'tippingcomp/templates/')


def help(request):
    return render(request, 'help.html')


def matches(request):
    ms = Match.objects.all()
    return render(request, 'matches.html', {"matches":add_match_info(get_user(request),ms), "title":"All Matches"})


def upcoming_matches(request):
    ms = Match.objects.all()
    ms = [match for match in ms if not match.begun()]
    ms = sorted(ms, key=lambda a:a.date)[:15]
    return render(request, 'matches.html', {"matches":add_match_info(get_user(request),ms), "title":"Upcoming Matches"})


def recent_matches(request):
    ms = Match.objects.all()
    ms = [match for match in ms if match.begun()]
    ms = sorted(ms, key=lambda a:a.date)[:15]

    return render(request, 'matches.html', {"matches":add_match_info(get_user(request),ms), "title":"Recent Matches"})


def match(request, id):
    match = Match.objects.get(id=id)
    try:
        bet = Bet.objects.get(match=match, user=get_user(request))
        bet = f"You bet on {bet.match.hteam if bet.bet else bet.match.ateam}. "
    except:
        bet = "You haven't bet on this game. " 

    if match.begun():
        bet += "Bets have now closed."
    else:
        bet += "Bets are still open."

    return render(
        request, 
        "match.html",
        {
            "match": match, 
            "date": match.date.strftime("%a %-d %b"),
            "time": match.date.strftime("%-I:%M%p").lower(),
            "bet": bet,
        }
    )


def bet(request, id: int, homeoraway: str) -> HttpResponse:
    if homeoraway not in ('home' 'away'): redirect(f"/tippingcomp/matches/{id}/")
    user = get_user(request)
    if not user.is_authenticated:
        return redirect(f"/tippingcomp/login/")
    try:
        user = User.objects.get(first_name=user.first_name, last_name=user.last_name)
    except User.DoesNotExist:
        return redirect(f"/tippingcomp/login/")

    match = Match.objects.get(id=id)
    if match.begun():
        return redirect(f"/tippingcomp/matches/{id}/")

    bet = Bet.objects.filter(user=user, match=match)
    if bet: bet.delete()

    b = Bet(user=user, match=match, bet=(homeoraway == "home"))
    b.save()

    return redirect(f"/tippingcomp/matches/{id}/")


def scoreboard(request):
    users = User.objects.all()
    return render(request, 'scoreboard.html', {'users':sorted(users, key=lambda u: u.score, reverse=True)})


def showuser(request, name):
    _user = User.objects.get(first_name=name)
    rounds = list()
    matches = [match for match in Match.objects.all() if match.complete]
    for round in range(1, 24):
        round_results = []
        for match in matches:
            if match.round == round:
                teams = match.hteam, match.ateam
                try:
                    b: Bet = Bet.objects.get(user=_user, match=match)
                    s = f"Picked {teams[b.bet]} over {teams[not b.bet]} and {'won' if b.result else 'lost'}"
                except:
                    s = f"Didn't bet on {teams[0]} vs {teams[1]}, got {teams[1]} by default and {'won' if match.winnerteamid == match.ateamid else 'lost'}"
                round_results.append(s)

        if round_results:
            round_results.insert(0, f"Round {round}")
            rounds.append(round_results)

    if not rounds:
        rounds = [[name + " hasn't made any bets yet."]]
        
    return render(request, "user.html", {"user":_user,"bets": rounds})
