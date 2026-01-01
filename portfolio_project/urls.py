from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import path

def healthz(request):
    return HttpResponse("OK")

urlpatterns = [
    path("healthz", healthz),
]

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('apps.public.urls')),
    path('admin/', include('apps.admin_panel.urls')),
    path('accounts/', include('apps.accounts.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)