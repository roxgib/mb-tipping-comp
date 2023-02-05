# Todo
# - User Agent

from __future__ import annotations

from requests import get
import json

from flask_sqlalchemy import SQLAlchemy, session

from .app import app, db
from .models import Match, Team, Bet, User

SQUIGGLE = "https://api.squiggle.com.au/"
YEAR = "2023"


def get_from_squiggle(params: dict) -> dict:
    """Get data from the Squiggle API"""
    return json.loads(get(SQUIGGLE, params).text)


def get_teams() -> list[dict]:
    """Fetch the list of teams from Squiggle"""
    return get_from_squiggle({"q": "teams"})["teams"]


def get_matches(year=YEAR, rnd=None, game=None, complete=None):
    params = {
        "q": "games",
        "year": year,
        "round": rnd,
        "game": game,
        "complete": complete,
    }
    return get_from_squiggle(params)["games"]


def get_tips(year=YEAR, rnd=None, game=None, complete=None):
    params = {
        "q": "tips",
        "year": year,
        "round": rnd,
        "game": game,
        "complete": complete,
    }
    return get_from_squiggle(params)["tips"]


def update():
    """Pull updated match and result information from Squiggle"""
    updated_matches = get_matches()

    with app.app_context():
        for match in updated_matches[::-1]:
            if match["hteamid"] is None or match["ateamid"] is None:
                continue
            match["home_team_key"] = Team.query.filter_by(id=match["hteamid"]).first().id
            match["away_team_key"] = Team.query.filter_by(id=match["ateamid"]).first().id
            match["complete"] = True if match["complete"] == 100 else False

            try:
                umatch = Match.query.filter_by(id=match["id"]).first()
            except Match.DoesNotExist:
                umatch = None
            if umatch:
                for key, value in match.items():
                    setattr(umatch, key, value)
            else:
                m = Match(**match)
                db.session.add(m)

        bets = Bet.query.all()
        for bet in bets:
            bet.updateResult()

        users = User.query.all()
        for user in users:
            user.updateScore()

        db.session.commit()


def update_teams():
    """Update the list of teams in the database"""
    updated_teams = get_teams()
    with app.app_context():
        teams = Team.query.all()
        teams = {team.id: team for team in teams}
        for uteam in updated_teams:
            if uteam["retirement"] != 9999:
                continue
            if uteam["id"] not in teams:
                _team = Team(**uteam)
                db.session.add(_team)
        db.session.commit()


if __name__ == "__main__":
    update_teams()
    update()

# if __name__ == "__main__":
#     import subprocess

#     teams = get_teams()
#     for team in teams:
#         url = f"https://squiggle.com.au{team['logo']}"
#         subprocess.run(["curl", "-O", url])
