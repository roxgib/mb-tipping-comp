from app import app, db, login_manager
from squiggle import update, update_teams
from funcs import add_match_info

import flask
from flask import render_template, request, redirect, url_for, Response, session, abort
import flask_login
from flask_login import login_user, logout_user, login_required

from models import Bet, Match, Team, User


@app.route("/tippingcomp/")
def index():
    """Renders the home page."""
    users = sorted(User.query.all(), key=lambda u: u.score, reverse=True)
    next_match = Match.query.filter_by(complete=False).first()
    return render_template("index.html", users=users[:3], match=next_match)


@app.route("/tippingcomp/help/")
def help():
    """Renders the help page."""
    return render_template("help.html")


@app.route("/tippingcomp/matches/")
def matches():
    """Renders the matches page."""
    ms = Match.query.all()
    return render_template(
        "matches.html",
        matches=add_match_info(flask_login.current_user, ms),
        title="All Matches",
    )


@app.route("/tippingcomp/matches/upcoming")
def upcoming_matches():
    ms = [match for match in Match.query.all() if not match.begun()]
    ms = sorted(ms, key=lambda a: a.date)[:15]
    return render_template(
        "matches.html",
        matches=add_match_info(flask_login.current_user, ms),
        title="Upcoming Matches",
    )


@app.route("/tippingcomp/matches/recent/")
def recent_matches():
    ms = [match for match in Match.query.all() if match.begun()]
    ms = sorted(ms, key=lambda a: a.date)[:15]

    return render_template(
        "matches.html",
        matches=add_match_info(flask_login.current_user, ms),
        title="Recent Matches",
    )


@app.route("/tippingcomp/matches/<int:id>/")
def match(id):
    match = Match.query.get(id)
    try:
        bet = Bet.query.get(match=match, user=flask_login.current_user)
        bet = f"You bet on {bet.match.hteam if bet.bet else bet.match.ateam}. "
    except:
        bet = "You haven't bet on this game. "

    if match.begun():
        bet += "Bets have now closed."
    else:
        bet += "Bets are still open."

    return render_template(
        "match.html",
        match=match,
        date=match.date.strftime("%a %-d %b"),
        time=match.date.strftime("%-I:%M%p").lower(),
        bet=bet,
    )


@app.route("/tippingcomp/matches/<int:id>/bet/<homeoraway>/")
@flask_login.login_required
def bet(id: int, homeoraway: str):
    if homeoraway not in ("home" "away"):
        redirect(f"/tippingcomp/matches/{id}/")
    user = flask_login.current_user()
    if not user.is_authenticated:
        return redirect(f"/tippingcomp/login/")
    try:
        user = User.query.get(first_name=user.first_name, last_name=user.last_name)
    except User.DoesNotExist:
        return redirect(f"/tippingcomp/login/")

    match = Match.query.get(id=id)
    if match.begun():
        return redirect(f"/tippingcomp/matches/{id}/")

    bet = Bet.query.filter(user=user, match=match)
    if bet:
        bet.delete()

    b = Bet(user=user, match=match, bet=(homeoraway == "home"))
    b.save()

    return redirect(f"/tippingcomp/matches/{id}/")


@app.route("/tippingcomp/scoreboard/")
def scoreboard():
    users = sorted(User.query.all(), key=lambda u: u.score, reverse=True)
    return render_template("scoreboard.html", users=users)


@app.route("/tippingcomp/user/<name>/")
@flask_login.login_required
def show_user(name):
    _user = User.query.get(first_name=name)
    rounds = list()
    matches = [match for match in Match.query.all() if match.complete]
    for round in range(1, 24):
        round_results = []
        for match in matches:
            if match.round == round:
                teams = match.hteam, match.ateam
                try:
                    b: Bet = Bet.query.get(user=_user, match=match)
                    s = f"Picked {teams[not b.bet]} over {teams[b.bet]} and {'won' if b.result else 'lost'}"
                except:
                    s = f"Didn't bet on {teams[0]} vs {teams[1]}, got {teams[1]} by default and {'won' if match.winnerteamid == match.ateamid else 'lost'}"
                round_results.append(s)

        if round_results:
            round_results.insert(0, f"Round {round}")
            rounds.append(round_results)

    if not rounds:
        rounds = [[name + " hasn't made any bets yet."]]
    return render_template("user.html", user=_user, bets=rounds)


@app.route("/tippingcomp/login/", methods=["GET", "POST"])
def login():
    form = flask_login.LoginForm()
    if request.method == "POST":
        login_user(flask_login.user, remember=True)

        flask.flash("Logged in successfully.")

        next = request.args.get("next")
        if not flask_login.is_safe_url(next):
            return flask.abort(400)

        return flask.redirect(next or flask.url_for("index"))
    else:
        return flask.render_template("login.html", form=form)


@app.route("/tippingcomp/logout/")
@login_required
def logout():
    logout_user()
    return redirect("/tippingcomp/login/")


@app.route("/tippingcomp/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.POST["username"]
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        password = request.POST["password"]
        confirmpassword = request.POST["confirmpassword"]
        if password != confirmpassword:
            return render_template("register.html", error="Passwords don't match.")
        if User.query.filter(username=username):
            return render_template("register.html", error="User already exists.")
        user = User(username=username, first_name=firstname, last_name=lastname)
        user.set_password(password)
        user.save()
        return redirect("/tippingcomp/login/")
    return render_template("register.html")
