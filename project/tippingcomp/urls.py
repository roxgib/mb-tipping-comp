from django.urls import include, path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('matches/', views.matches, name='matches'),
    path('matches/upcoming/', views.upcoming_matches, name='bet'),
    path('matches/recent/', views.recent_matches, name='bet'),
    path('matches/<int:id>/', views.match, name='match'),
    path('matches/<int:id>/bet/<str:homeoraway>/', views.bet, name='bet'),
    path('scoreboard/', views.scoreboard, name='scoreboard'),
    path('user/<str:name>/', views.showuser, name='user'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logos/<str:file>', views.logo, name='logo'),
    path('templates/<str:file>.css', views.css, name='css'),
    path('help/', views.help, name='help'),
]