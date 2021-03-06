from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from research.admin import research_site
from administration.admin import admin_site
from research.views import ResearchResultDownloadView

urlpatterns = [
    path('jet/', include('jet.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('research/', research_site.urls),
    path('admin/', admin_site.urls),
    path('', include('participate.urls', namespace='participate')),
    path('research/<str:research_hex>/download/', ResearchResultDownloadView.as_view(), name='get_result')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
