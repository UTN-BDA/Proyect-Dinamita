from django.urls import path, include
from .views import game_search

urlpatterns = [
    path('search/', game_search, name='game_search'),
]