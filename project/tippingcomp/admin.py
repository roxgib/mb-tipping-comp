from django.contrib import admin

# Register your models here.

from .models import User, Team, Match, Bet

admin.site.register(User)
admin.site.register(Team)
admin.site.register(Match)
admin.site.register(Bet)