from datetime import datetime, timedelta, timezone
from typing import List

from .models import Match, User, Bet

venues = {
    'Adelaide Oval',
    'Bellerive Oval',
    'Carrara',
    'Docklands',
    'Eureka Stadium',
    'Gabba',
    'Kardinia Park',
    'M.C.G.',
    'Manuka Oval',
    'Perth Stadium',
    'S.C.G.',
    'Stadium Australia',
    'Sydney Showground',
    'Traeger Park',
    'York Park',
    "Cazaly's Stadium",
}

def add_match_info(user: User, matches: List[Match]) -> List[Match]:
    for match in matches:
        try:
            bet = Bet.objects.get(match=match, user=user)
            match.has_bet = True
            match.bet_team = match.hteam if bet.bet else match.ateam
        except:
            match.has_bet = False

    for match in matches:
        match.hdate = match.date.strftime("%a %-d %b")
        match.htime = match.date.strftime("%-I:%M%p").lower()

        match.begun = match.begun()
    
    return matches


def tilly_bets():
    fav_teams = [
        "Sydney"
    ]