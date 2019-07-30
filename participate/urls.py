from django.urls import path, reverse

from participate.views import ResearchView, IndexView, ParticipateListView, \
    ParticipantSignupView, ParticipantLoginView, GameView, GameResultView, ParticipantLogoutView


app_name = 'participate'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('participate/', ParticipateListView.as_view(), name='particiaptelist'),
    path('research/<str:research_hex>/', ResearchView.as_view(), name='research'),
    path('research/<str:research_hex>/game/<int:game_id>/', GameView.as_view(), name='game'),
    path('research/<str:research_hex>/game/<int:game_id>/result/', GameResultView.as_view(), name='game_result'),
    path('user/signup/', ParticipantSignupView.as_view(), name='signup'),
    path('user/logout/', ParticipantLogoutView.as_view(), name='logout'),
    path('user/login/', ParticipantLoginView.as_view(), name='login')
]


