from django.urls import path, include
from .views import game_search, home, all, graphs_home, graphs_by_gender

urlpatterns = [
    path('', home, name='home'),
    path('search/', game_search, name='game_search'),
    path('all/', all, name='all_games'),
    path('graphs/', graphs_home, name='graphs_home'),
    path('graphs-by-gender/', graphs_by_gender, name='graphs_by_gender'),
]