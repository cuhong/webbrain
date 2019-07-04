from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from research.admin import research_site
from administration.admin import admin_site
from research.views import GameView

urlpatterns = [
    path('jet/', include('jet.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('research/', research_site.urls),
    path('admin/', admin_site.urls),
    path('participate/', include('participate.urls')),
    path('game_test/<int:research_id>/<int:game_id>/', GameView.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
