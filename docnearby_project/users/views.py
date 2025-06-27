# docnearby_project/users/views.py
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status, serializers # Import serializers for exception handling
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RegisterSerializer, UserSerializer, MyTokenObtainPairSerializer
from .models import UserProfile

# Registration View
class RegisterView(generics.CreateAPIView):
    """ Registers a new user (Patient or Provider). """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save() # Serializer .create handles User, UserProfile, ProviderProfile
            try:
                user_profile = UserProfile.objects.get(user=user)
                user_type_display = user_profile.get_user_type_display()
            except UserProfile.DoesNotExist:
                user_type_display = "User"
            response_data = {"message": f"{user_type_display} '{user.username}' registered successfully!"}
            headers = self.get_success_headers({}) # Get headers for 201 response
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
             print(f"Registration Validation Error: {e.detail}")
             return Response(e.detail, status=status.HTTP_400_BAD_REQUEST) # Return validation errors
        except Exception as e:
             print(f"Registration Creation Error: {type(e).__name__} - {e}")
             return Response({"error": "Registration failed due to an internal error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Login View
class MyTokenObtainPairView(TokenObtainPairView):
    """ Handles login, returns tokens + user details via custom serializer. """
    serializer_class = MyTokenObtainPairSerializer

# Get Current User View
class UserProfileView(generics.RetrieveAPIView):
    """ Returns profile data for the currently authenticated user. """
    permission_classes = (permissions.IsAuthenticated,) # Must be logged in
    serializer_class = UserSerializer # Returns User + nested Profile data

    def get_object(self):
        return self.request.user # Return the user associated with the request token