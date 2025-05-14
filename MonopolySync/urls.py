from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # Add this import
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/registration/', include("registration.urls")),
    path('api/user-profile/', include("userProfile.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
