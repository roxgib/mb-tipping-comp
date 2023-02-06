from datetime import datetime, timedelta, timezone
from email.utils import localtime
from time import strftime
import hashlib
import os

import flask_login

from app import db, login_manager


class Team(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200))
    abbrev = db.Column(db.String(200))
    logo = db.Column(db.String(200))
    retirement = db.Column(db.Integer)
    debut = db.Column(db.Integer)

    def __str__(self):
        return self.name


class User(db.Model, flask_login.UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password_hash = db.Column(db.String(500))
    salt = db.Column(db.String(100), default="")

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def score(self):
        matches = [match for match in Match.query.all() if match.complete]

        score = 0
        for match in matches:
            try:
                b: Bet = Bet.query.filter_by(user=self, match=match).first()
                result = b.result
            except:
                result = match.winnerteamid == match.ateamid
            if result:
                score += 1

        return score

    def get_id(self):
        return self.id

    @login_manager.user_loader
    def get_user(id):
        return User.query.get(id)

    def set_password(self, password: str):
        self.salt = os.urandom(18).hex()
        self.password_hash = self._hash_password(password)

    def check_password(self, password: str) -> bool:
        return self._hash_password(password) == self.password_hash

    def _hash_password(self, password: str) -> str:
        key = hashlib.pbkdf2_hmac(
            "sha512",
            password.encode("utf-8"),
            self.salt.encode("utf-8"),
            100_000,
            dklen=128,
        )
        return key.hex()


class Match(db.Model):
    __tablename__ = "matches"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    updated = db.Column(db.Date)
    round = db.Column(db.Integer)
    roundname = db.Column(db.String(200))
    tz = db.Column(db.String(200))
    venue = db.Column(db.String(200))
    date = db.Column(db.Date)
    hteam = db.Column(db.String(200))
    ateam = db.Column(db.String(200))
    hteamid = db.Column(db.Integer)
    ateamid = db.Column(db.Integer)
    home_team_key = db.Column(db.Integer, db.ForeignKey("teams.id"))
    away_team_key = db.Column(db.Integer, db.ForeignKey("teams.id"))
    winnerteamid = db.Column(db.Integer, db.ForeignKey("teams.id"))
    winner = db.Column(db.Boolean)
    hscore = db.Column(db.Integer)
    hgoals = db.Column(db.Integer)
    hbehinds = db.Column(db.Integer)
    ascore = db.Column(db.Integer)
    agoals = db.Column(db.Integer)
    abehinds = db.Column(db.Integer)
    is_grand_final = db.Column(db.Boolean, default=False)
    is_final = db.Column(db.Integer)
    year = db.Column(db.Integer, default=2022)
    complete = db.Column(db.Boolean, default=False)
    timestr = db.Column(db.String(200))
    localtime = db.Column(db.Date)
    unixtime = db.Column(db.Integer)

    def __str__(self):
        return f"{self.home_team_key.abbrev} vs. {self.away_team_key.abbrev}, {self.date.strftime('%a %-d %b')} (R{self.round})"

    def datetime(self) -> datetime:
        return datetime.fromtimestamp(self.unixtime, timezone.utc)

    def begun(self) -> bool:
        return self.datetime() < datetime.now(timezone.utc)

    def away_team(self):
        return Team.query.get(self.away_team_key)

    def home_team(self):
        return Team.query.get(self.home_team_key)

    class Meta:
        verbose_name_plural = "Matches"


class Bet(db.Model):
    __tablename__ = "bets"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.Integer, db.ForeignKey("users.id"))
    match = db.Column(db.Integer, db.ForeignKey("matches.id"))
    # True -> Home Team, False -> Away Team
    bet = db.Column(db.Boolean)

    def __str__(self):
        return f"{self.user.first_name} {self.match} {self.match.hteam if self.bet else self.match.ateam}"

    @property
    def result(self):
        if self.match.complete and self.match.winnerteamid is not None:
            return (self.match.winnerteamid == self.match.hteamid) == self.bet
        else:
            return None
