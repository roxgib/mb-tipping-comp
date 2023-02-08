import json

from app import app, db, login_manager
from squiggle import update, update_teams

import flask
from flask import render_template, request, redirect, url_for, Response, session, abort
import flask_login
from flask_login import login_user, logout_user, login_required
import sqlalchemy

from models import Bet, Match, Team, User


@app.route("/")
def _index():
    return redirect(url_for("index"))


@app.route("/tippingcomp/")
def index():
    """Renders the home page."""
    users = sorted(User.query.all(), key=lambda u: u.score, reverse=True)
    next_match = (
        Match.query.filter(Match.complete == False).order_by(Match.date).first()
    )
    return render_template("index.html", users=users[:5], match=next_match)


@app.route("/tippingcomp/help/")
def help():
    """Renders the help page."""
    return render_template("help.html")


@app.route("/tippingcomp/matches/")
def matches():
    """Renders the matches page."""
    return render_template(
        "matches.html",
        matches=Match.query.all(),
        title="All Matches",
    )


@app.route("/tippingcomp/matches/upcoming")
def upcoming_matches():
    ms = [match for match in Match.query.all() if not match.has_begun]
    return render_template(
        "matches.html",
        matches=sorted(ms, key=lambda a: a.date)[:15],
        title="Upcoming Matches",
    )


@app.route("/tippingcomp/matches/recent/")
def recent_matches():
    ms = [match for match in Match.query.all() if match.has_begun]
    ms = sorted(ms, key=lambda a: a.date)[:15]

    return render_template(
        "matches.html",
        matches=ms,
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

    if match.has_begun():
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
    if homeoraway not in ("home", "away"):
        redirect(f"/tippingcomp/matches/{id}/")
    user = flask_login.current_user
    if not user.is_authenticated:
        return redirect(f"/tippingcomp/login/")

    match = Match.query.get(id)
    if match.has_begun:
        return redirect(f"/tippingcomp/matches/{id}/")

    db.session.query(Bet).filter(Bet.user == user.id, Bet.match == match.id).delete()
    b = Bet(user=user.id, match=match.id, bet=(homeoraway == "home"))
    db.session.add(b)
    db.session.commit()

    return (
        json.dumps({"success": True, "team": b.chosen_team.name}),
        200,
        {"ContentType": "application/json"},
    )


@app.route("/tippingcomp/scoreboard/")
def scoreboard():
    users = sorted(User.query.all(), key=lambda u: u.score, reverse=True)
    return render_template("scoreboard.html", users=users)


@app.route("/tippingcomp/user/<int:id>/")
@flask_login.login_required
def show_user(id: int):
    _user = User.query.get(id)
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
        rounds = [[_user.first_name + " hasn't made any bets yet."]]
    return render_template("user.html", user=_user, bets=rounds)


@app.route("/tippingcomp/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return flask.render_template("login.html", next=request.args.get("next"))
    email = request.form["email"]
    password = request.form["password"]
    user = User.query.filter(User.email == email).first()
    if not user:
        return flask.render_template(
            "login.html",
            next=request.args.get("next"),
            error="User not found. Did you type the email address correctly?",
        )
    if not user.check_password(password):
        return flask.render_template(
            "login.html",
            next=request.args.get("next"),
            error="Incorrect password.",
        )
    login_user(user, remember=True)
    next = request.args.get("next")
    return flask.redirect(next or flask.url_for("index"))


@app.route("/tippingcomp/logout/")
@login_required
def logout():
    logout_user()
    return redirect("/tippingcomp/login/")


@app.route("/tippingcomp/register/", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    email = request.form["email"]
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    password = request.form["password"]
    confirmpassword = request.form["confirmpassword"]
    if password != confirmpassword:
        return render_template("register.html", error="Passwords don't match.")
    if (
        User.query.filter_by(email=email).first()
        or User.query.filter_by(first_name=firstname, last_name=lastname).first()
    ):
        return render_template("register.html", error="User already exists.")
    user = User(email=email, first_name=firstname, last_name=lastname)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return redirect("/tippingcomp/login/")
