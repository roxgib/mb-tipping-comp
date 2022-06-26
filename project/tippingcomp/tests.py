from datetime import datetime
from django.test import TestCase

from .models import User, Team, Match, Bet
from .squiggle import getMatches


class ModelTests(TestCase):
    def setUp(self):
        self.user = User(
            username = 'test',
            first_name = 'first',
            last_name = 'last',
            email = 'samjr.bradshaw@gmail.com'
            )

        self.team1 = Team(id = 1, name = f"Test Team {1}", abbrev = f"TT{1}", retirement = 9999)
        self.team2 = Team(id = 2, name = f"Test Team {2}", abbrev = f"TT{2}", retirement = 9999)

        self.match = Match(
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
            home_team_key = self.team1,
            away_team_key = self.team2,
            year = 2022,
            complete = False,
            localtime = "2022-01-01 12:00",
        )

        self.user.save()
        self.team1.save()
        self.team2.save()
        self.match.save()

    def test_create_team(self):
        team = Team(id = 1, name = "Test Team", abbrev = "TTM", retirement = 9999)
        self.assertEquals(str(team), "Test Team")

    def test_create_user(self):
        user = User(username = 'test_username', first_name = 'test2', 
                    last_name='test3', email = 'test@gmail.com')
        self.assertEqual(str(user), "test2 test3")
        self.assertEqual(user.email, "test@gmail.com")
        self.assertEqual(user.username, 'test_username')

    def test_create_match(self):
        match = Match(
            id = 2, 
            round = 2,
            roundname = "Round 2",
            tz = '+10',
            venue = 'SCG',
            date = datetime(2022,5,1),
            hteam = "Team 1",
            ateam = "Team 2",
            hteamid = 1,
            ateamid = 2,
            home_team_key = self.team1,
            away_team_key = self.team2,
            year = 2022,
            complete = False,
            localtime = "2022-05-01 12:00",
        )
        
        self.assertEquals(str(match),"TT1 vs. TT2, Sun 1 May (R2)")
        self.assertIs(self.match.home_team_key, self.team1)
        self.assertIs(self.match.away_team_key, self.team2)

    def test_create_bet(self):
        bet = Bet(user=self.user, match=self.match, bet=True)
        bet.save()
        self.assertEqual(str(bet), "first TT1 vs. TT2, Wed 16 Mar (R1) Team 1")
        self.assertEqual(Bet.objects.get(match=self.match), bet)

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
        self.assertEquals(match.complete, 100)
        self.assertEquals(match.localtime, '2022-03-16 19:10:00')

class TimeHandlingTests(TestCase):
    def test_match_local_time(self):
        match = Match(**getMatches(game="8662")[0])
        #FIXME: these aren't implemented yet
        # self.assertEquals(match.timezones(), datetime)
        # self.assertEquals(match.utc_datetime(), datetime(2022, 3, 16, 19, 10, 00))

