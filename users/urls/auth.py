from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from users.views.auth import RegisterView, LogoutView, UserMe, CustomTokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserMe.as_view(), name='me'),
] 