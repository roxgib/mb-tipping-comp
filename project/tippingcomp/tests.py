from datetime import datetime
from django.test import TestCase

from .models import *
from .squiggle import *

def create_test_user():
    user = User(username = 'test', first_name = 'first', last_name='last', email = 'samjr.bradshaw@gmail.com')
    return user

def create_test_team(index):
    team = Team(id = index, name = f"Test Team {index}", abbrev = f"TT{index}", retirement = 9999)
    return team

def create_test_match(team1, team2):
        match = Match(
            id = 1, 
            round = 1,
            roundname = "Round 1",
            tz = '+10',
            venue = 'SCG',
            date = datetime(2022,3,16),
            hteam = "Team 1",
            ateam = "Team 2",
            hteamid = 1,
            ateamid = 2,
            home_team_key = team1,
            away_team_key = team2,
            year = 2022,
            complete = False,
            localtime = "19:10",
        )
        return match

class ModelTests(TestCase):
    def test_create_team(self):
        team = Team(id = 1, name = "Test Team", abbrev = "TTM", retirement = 9999)
        self.assertEquals(str(team), "Test Team")

    def test_create_user(self):
        user = User(username = 'test', first_name = 'first', last_name='last', email = 'samjr.bradshaw@gmail.com')
        self.assertEquals(str(user), "first last")

    def test_create_match(self):
        team1 = create_test_team(1)
        team2 = create_test_team(2)
        match = create_test_match(team1, team2)
        self.assertEquals(str(match),"TT1 vs. TT2, Wed 16 Mar (R1)")
        self.assertIs(match.home_team_key, team1)
        self.assertIs(match.away_team_key, team2)

    def test_create_bet(self):
        user = create_test_user()
        team1 = create_test_team(1)
        team2 = create_test_team(2)
        match = create_test_match(team1, team2)
        bet = Bet(user=user, match=match, bet=True)
        self.assertEquals(str(bet), "first TT1 vs. TT2, Wed 16 Mar (R1) Team 1")


class SquiggleTests(TestCase):
    def test_get_matches(self):
        match = Match(**getMatches(game="8662")[0])
        self.assertEquals(match.hteam, "Melbourne")
        self.assertEquals(match.ateam, "Western Bulldogs")
        self.assertEquals(match.id, 8662)
        self.assertEquals(match.round, 1)
        self.assertEquals(match.roundname, "Round 1")
        self.assertEquals(match.tz, "+11:00")
        self.assertEquals(match.venue, "M.C.G.")
        self.assertEquals(match.date, datetime(2022, 3, 16, 19, 10, 0).strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEquals(match.is_grand_final, False)
        self.assertEquals(match.is_final, False)
        self.assertEquals(match.year, 2022)
        self.assertEquals(match.complete, False)
        self.assertEquals(match.localtime, '2022-03-16 19:10:00')


class TimeHandlingTests(TestCase):
    def test_match_local_time(self):
        match = Match(**getMatches(game="8662")[0])
        self.assertEquals(match.timezones(), datetime)
        self.assertEquals(match.utc_datetime(), datetime(2022, 3, 16, 19, 10, 00))

