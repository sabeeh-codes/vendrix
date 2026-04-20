from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, EmailLoginView, ProfileView

urlpatterns = [
    path('register/',      RegisterView.as_view(),    name='register'),
    path('login/',         EmailLoginView.as_view(),  name='login'),      # ✅ now returns username + email
    path('token/refresh/', TokenRefreshView.as_view(),name='token_refresh'),
    path('profile/',       ProfileView.as_view(),     name='profile'),
]