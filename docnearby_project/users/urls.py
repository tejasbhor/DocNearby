# docnearby_project/users/urls.py
from django.urls import path
from .views import RegisterView, MyTokenObtainPairView, UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'users' # Define app namespace

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'), # Custom login view
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Standard refresh view
    path('register/', RegisterView.as_view(), name='auth_register'),         # Registration view
    path('user/me/', UserProfileView.as_view(), name='user_profile'),        # Get current user view
]