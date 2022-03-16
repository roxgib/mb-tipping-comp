from datetime import datetime, timedelta, timezone
from email.utils import localtime
from operator import mod
from time import strftime
from typing import Union
from django.db import models

from django.contrib.auth.models import User as dUser
import pytz

class Team(models.Model):
    id = models.IntegerField('ID', primary_key=True)
    name = models.CharField('Name', max_length=200, default=None, blank=True, null=True)
    abbrev = models.CharField('Abbreviation', max_length=200, default=None, blank=True, null=True)
    logo = models.CharField('Logo',  max_length=200, default=None, blank=True, null=True)
    retirement = models.IntegerField("Retirement", default=None, blank=True, null=True)
    debut = models.IntegerField("Debut", default=None, blank=True, null=True)

    def __str__(self):
        return self.name

class User(dUser):
    fav_team = models.ForeignKey(Team, verbose_name="Favourite Team", on_delete=models.CASCADE, default=None, blank=True, null=True)
    score = models.IntegerField("Score", default=0)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def updateScore(self):
        bets = Bet.objects.all()
        bets = [bet for bet in bets if bet.user is self]

        score = 0
        for bet in bets:
            if bet.result:
                score += 1
        
        self.score = score
        self.save()


class Match(models.Model):
    id = models.IntegerField('ID', primary_key=True)
    updated = models.DateTimeField('Updated', default=None, blank=True, null=True)
    round = models.IntegerField('Round', default=None, blank=True, null=True)
    roundname = models.CharField('Round Name', max_length=100, default=None, blank=True, null=True)
    tz = models.CharField('Timezone', max_length=100, default=None, blank=True, null=True)
    venue = models.CharField('Venue', max_length=200,default=None, blank=True, null=True)
    date = models.DateTimeField('Match Date', default=None, blank=True, null=True)
    hteam = models.CharField("Home Team", max_length=200, default=None, blank=True, null=True)
    ateam = models.CharField("Away Team", max_length=200, default=None, blank=True, null=True)
    hteamid = models.IntegerField("Home Team ID", default=None, blank=True, null=True)
    ateamid = models.IntegerField("Away Team ID", default=None, blank=True, null=True)
    home_team_key = models.ForeignKey(Team, verbose_name="Home Team Key", related_name='home_team', on_delete=models.CASCADE, default=None, blank=True, null=True)
    away_team_key = models.ForeignKey(Team, verbose_name="Away Team Key", related_name='away_team', on_delete=models.CASCADE, default=None, blank=True, null=True)
    winnerteamid = models.IntegerField("Winner Team ID", default=None, blank=True, null=True)
    winner = models.CharField("Winner", max_length=200, default=None, blank=True, null=True)
    hscore = models.IntegerField('Home Team Score', default=None, blank=True, null=True)
    hgoals = models.IntegerField('Home Team Goals', default=None, blank=True, null=True)
    hbehinds = models.IntegerField('Home Team Behinds', default=None, blank=True, null=True)
    ascore = models.IntegerField('Away Team Score', default=None, blank=True, null=True)
    agoals = models.IntegerField('Away Team Goals', default=None, blank=True, null=True)
    abehinds = models.IntegerField('Away Team Behinds', default=None, blank=True, null=True)
    is_grand_final = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)
    year = models.IntegerField(default=2022)
    complete = models.BooleanField(default=False)
    localtime = models.DateTimeField('Local Time', default=None, blank=True, null=True)

    def __str__(self):
        return f"{self.home_team_key.abbrev} vs. {self.away_team_key.abbrev}, {self.date.strftime('%a %-d %b')} (R{self.round})"

    def datetime(self) -> datetime:
        date = datetime.strptime(str(self.localtime)[:-6]+self.tz.replace(':',''), "%Y-%m-%d %H:%M:%S%z")
        return date

    def begun(self) -> bool:
        return self.datetime() < datetime.now(timezone.utc)

    class Meta:
        verbose_name_plural = 'Matches'
    

class Bet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, blank=True, null=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, default=None, blank=True, null=True)
    bet = models.BooleanField("Bet", max_length=200) # True -> Home Team, False -> Away Team
    result = models.IntegerField("Result", default=None, blank=True, null=True) 
    # 0 -> bet not made 
    #  1 -> match not over 
    #  2 -> correct 
    #  3 -> incorrect 
    #  4 -> draw 
    #  5 -> bet too late

    def __str__(self):
        return f"{self.user.first_name} {self.match} {self.match.hteam if self.bet else self.match.ateam}"

    def update(self):
        pass