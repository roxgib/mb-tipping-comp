# Todo
# - User Agent

from __future__ import annotations

from requests import get
import json


# if __name__ != '__main__':
from .models import Match, Team, Bet, User

SQUIGGLE = 'https://api.squiggle.com.au/'
YEAR = '2022'

def get_from_squiggle(params: dict) -> dict:
    """Get data from the Squiggle API"""
    response = get(SQUIGGLE, params).text
    return json.loads(response)

def get_teams() -> list[dict]:
    """Fetch the list of teams from Squiggle"""
    params = {
        'q':'teams'
    }

    return get_from_squiggle(params)['teams']

def get_matches(year=YEAR, rnd=None, game=None, complete=None):
    params = {
        'q':        'games',
        'year':     year,
        'round':    rnd,
        'game':     game,
        'complete': complete,
    }

    return get_from_squiggle(params)['games']


def get_tips(year=YEAR, rnd=None, game=None, complete=None):
    params = {
        'q':        'tips',
        'year':     year,
        'round':    rnd,
        'game':     game,
        'complete': complete,
    }

    return get_from_squiggle(params)['tips']


def get_standings(year=YEAR, rnd=None):
    params = {
        'q':        'standings',
        'year':     year,
        'round':    rnd,
    }

    return get_from_squiggle(params)['standings']


def get_ladder(year=YEAR, rnd=None, source=None):
    params = {
        'q':        'standings',
        'year':     year,
        'round':    rnd,
        'source':   source
    }

    return get_from_squiggle(params)['standings']


def get_player_value(firstname=None,surname=None,name=None,match=None,year=None,team=None):
    params = {
        'firstname': firstname,
        'surname':surname,
        'name':name,
        'match':match,
        'year':year,
        'team':team,
    }

    return get_from_squiggle(params)['standings']


def update():
    """Pull updated match and result information from Squiggle"""
    updated_matches = get_matches()

    for match in updated_matches[::-1]:
        if match['hteamid'] is None or match['ateamid'] is None:
            continue
        match['home_team_key'] =  Team.objects.get(id=match['hteamid'])
        match['away_team_key'] =  Team.objects.get(id=match['ateamid'])
        match['complete'] = True if match['complete'] == 100 else False

        try:
            umatch = Match.objects.get(id=match['id'])
        except Match.DoesNotExist:
            umatch = None 
        if umatch:
            for key, value in match.items():
                setattr(umatch, key, value)
            umatch.save()
        else:
            print(match)
            m = Match(**match)
            m.save()

    bets = Bet.objects.all()
    for bet in bets:
        bet.updateResult()

    users = User.objects.all()
    for user in users:
        user.updateScore()

def update_teams():
    """Update the list of teams in the database"""
    updated_teams = get_teams()
    teams = Team.objects.all()

    for uteam in updated_teams:
        if uteam['retirement'] != 9999:
            continue
        if uteam['id'] in teams:
            pass
        else:
            _team = Team(**uteam)
            _team.save()


if __name__ == '__main__':
    import subprocess
    teams = get_teams()
    for team in teams:
        url = f"https://squiggle.com.au{team['logo']}"
        subprocess.run(['curl', '-O', url])