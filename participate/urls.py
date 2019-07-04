from django.urls import path

from participate.views import ParticipateView
from research.admin import research_site

app_name = 'participate'
urlpatterns = [
    path('<str:research_hex>/', ParticipateView.as_view(), name='index')
]


