from django.urls import path, include
from .views import game_search, home, all

urlpatterns = [
    path('', home, name='home'),
    path('search/', game_search, name='game_search'),
    path('all/', all, name='all_games'),
]