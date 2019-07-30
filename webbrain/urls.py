from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from research.admin import research_site
from administration.admin import admin_site

urlpatterns = [
    path('jet/', include('jet.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('research/', research_site.urls),
    path('admin/', admin_site.urls),
    path('', include('participate.urls', namespace='participate')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
