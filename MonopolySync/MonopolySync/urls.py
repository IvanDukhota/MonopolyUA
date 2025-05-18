
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('registration.urls')),
    path('profile/', include('user_profile.urls')),
    path('friends/', include('friends.urls')),
    path('notifications/', include('notifications.urls')),
    path('statistic/',include('gamedata.urls')),
    path('market/', include('items.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
