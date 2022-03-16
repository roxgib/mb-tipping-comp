
from django.contrib.auth import authenticate, get_user
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.static import serve

from .models import Bet, Match, Team, User
from .squiggle import updateMatches, updateTeams


def index(request):
    return render(request, 'index.html')


def logo(request, file):
    filepath = 'tippingcomp/logos/'
    return serve(request, file, filepath)


def css(request, file):
    return serve(request, file + '.css', 'tippingcomp/templates/')


def help(request):
    return render(request, 'help.html')


def matches(request):
    ms = Match.objects.all()
    return render(request, 'matches.html', {"matches":ms, "title":"All Matches"})


def upcoming_matches(request):
    ms = Match.objects.all()
    ms = [match for match in ms if match.date > timezone.now()]
    return render(request, 'matches.html', {"matches":ms, "title":"Upcoming Matches"})


def recent_matches(request):
    ms = Match.objects.all()
    ms = [match for match in ms if match.date < timezone.now()]
    return render(request, 'matches.html', {"matches":ms, "title":"Recent Matches"})


def match(request, id):
    match = Match.objects.get(id=id)
    try:
        bet = Bet.objects.get(match=match, user=get_user(request))
        bet = "You have bet on " + (bet.match.hteam if bet.bet else bet.match.ateam)
    except:
        bet = "You waited too long to be on this game" if match.complete else "You haven't bet on this game yet" 
    return render(
        request, 
        "match.html",
        {
            "match": match, 
            "date": match.date.strftime("%a %-d %b"),
            "time": match.date.strftime("%-I:%M%p"),
            "bet": bet,
        }
    )


def bet(request, id: int, homeoraway: str) -> HttpResponse:
    if homeoraway != "home" and homeoraway != "away": return HttpResponse("Error")
    homeoraway = True if homeoraway == "home" else False
    user = get_user(request)
    user = User.objects.get(first_name=user.first_name)
    if not user.is_authenticated:
        return HttpResponse('You need to login to bet. Click <a href="login">here</a> to login')
    
    match = Match.objects.get(id=id)
    if match.complete:
        return redirect(f"/tippingcomp/matches/{id}/")

    bet = Bet.objects.filter(user=user, match=match)
    if bet: bet.delete()

    b = Bet(user=user, match=match, bet=homeoraway)
    b.update()
    b.save()

    return redirect(f"/tippingcomp/matches/{id}/")


def scoreboard(request):
    users = User.objects.all()
    return render(request, 'scoreboard.html', {'users':sorted(users, key=lambda u:u.score)})


def showuser(request, name):
    _user = User.objects.get(first_name=name)
    bets = Bet.objects.all()
    bets = [bet for bet in bets if bet.user == _user]
    rounds = []
    for i in range(1, 24):
        round = [f'{bet.match.hteam if bet.bet else bet.match.ateam} over {bet.match.ateam if bet.bet else bet.match.hteam}' for bet in bets if (bet.match.round == i) and bet.match.complete]

        if round:
            round.insert(0, f"Round {i}")
            rounds.append(round)

    if not rounds:
        rounds = [[name + " hasn't made any bets yet."]]
        
    return render(request, "user.html", {"user":_user,"bets": rounds})
