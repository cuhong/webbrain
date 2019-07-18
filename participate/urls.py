from django.urls import path

from participate.views import ParticipateView, IndexView, ParticipateListView, ParticipateGameView
from research.admin import research_site

app_name = 'participate'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('participate/', ParticipateListView.as_view(), name='particiaptelist'),
    path('<str:research_hex>/', ParticipateView.as_view(), name='research'),
    path('<str:research_hex>/<int:game_id>/', ParticipateGameView.as_view(), name='game')
]


