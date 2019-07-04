from django.urls import path

from participate.views import ParticipateView
from research.admin import research_site

urlpatterns = [
    path('<str:research_hex>/', ParticipateView.as_view())
]


