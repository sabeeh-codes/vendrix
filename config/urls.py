from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# jwt auth urls
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # jwt auth (LOGIN)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # api routes
    path('api/auth/', include('users.urls')),
    path('api/', include('products.urls')),
    path('api/', include('orders.urls')),
]

# serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)