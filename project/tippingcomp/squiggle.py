# Todo
# - User Agent

from requests import get
import json

if __name__ != '__main__':
    from .models import Match, Team

squiggle = 'https://api.squiggle.com.au/'

def getTeams():
    params = {
        'q':'teams'
    }

    m = get(squiggle, params).text
    result = json.loads(m)['teams']

    return result


def getMatches(year='2022', round=None, game=None, complete=None):
    params = {
        'q':        'games',
        'year':     year,
        'round':    round,
        'game':     game,
        'complete': complete,
    }

    m = get(squiggle, params).text
    result = json.loads(m)['games']

    return result


def getTips(year='2022', round=None, game=None, complete=None):
    params = {
        'q':        'tips',
        'year':     year,
        'round':    round,
        'game':     game,
        'complete': complete,
    }

    m = get(squiggle, params).text
    result = json.loads(m)['tips']

    return result


def getStandings(year='2022', round=None):
    params = {
        'q':        'standings',
        'year':     year,
        'round':    round,
    }

    m = get(squiggle, params).text
    result = json.loads(m)['standings']

    return result


def getLadder(year='2022', round=None, source=None):
    params = {
        'q':        'standings',
        'year':     year,
        'round':    round,
        'source':   source
    }

    m = get(squiggle, params).text
    result = json.loads(m)['standings']

    return result


def getPlayerValue(firstname=None,surname=None,name=None,match=None,year=None,team=None):
    params = {
        'firstname': firstname,
        'surname':surname,
        'name':name,
        'match':match,
        'year':year,
        'team':team,
    }

    m = get(squiggle, params).text
    result = json.loads(m)['standings']

    return result


def updateMatches():
    updated_matches = getMatches()

    for match in updated_matches[::-1]:
        match['home_team_key'] =  Team.objects.get(name=match['hteam'])
        match['away_team_key'] =  Team.objects.get(name=match['ateam'])
        if umatch := Match.objects.get(id=match['id']):
            if not match['updated'] == umatch.updated:
                for key, value in match.items():
                    umatch[key] = value
                umatch.save()
        else:
            m = Match(**match)
            m.save()


def updateTeams():
    updated_teams = getTeams()
    teams = Team.objects.all()

    for team in updated_teams:
        if team['retirement'] != 9999: continue
        if team['id'] in teams:
            pass
        else:
            t = Team(**team)
            t.save()

if __name__ == '__main__':
    import subprocess
    teams = getTeams()
    for team in teams:
        url = f"https://squiggle.com.au{team['logo']}"
        subprocess.run(['curl', '-O', url])