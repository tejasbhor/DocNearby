# docnearby_project/users/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, ProviderProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# --- Nested Display Serializers ---
class ProviderProfileSerializer(serializers.ModelSerializer):
    """ For displaying ProviderProfile details when nested. """
    class Meta:
        model = ProviderProfile
        fields = ['specialization', 'clinic_name', 'address', 'latitude', 'longitude', 'operating_hours', 'is_verified', 'qualifications', 'bio']
        read_only_fields = fields

class UserProfileSerializer(serializers.ModelSerializer):
    """ For displaying UserProfile details (including nested Provider) when nested. """
    provider_details = ProviderProfileSerializer(read_only=True, required=False)
    role = serializers.CharField(source='user_type', read_only=True) # Map field name
    class Meta:
        model = UserProfile
        fields = ['id', 'phone_number', 'role', 'provider_details']
        read_only_fields = fields

# --- User Display Serializer ---
class UserSerializer(serializers.ModelSerializer):
    """ For displaying User details, including nested profile. """
    profile = UserProfileSerializer(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'name', 'profile']
        read_only_fields = fields
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

# --- Registration Serializer ---
class RegisterSerializer(serializers.Serializer):
    """ Handles registration input validation and creates User, UserProfile, ProviderProfile. """
    # User fields
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    # UserProfile fields
    user_type = serializers.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES, required=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    # ProviderProfile fields (optional inputs)
    specialization = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True, style={'base_template': 'textarea.html'})
    clinic_name = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=150)
    operating_hours = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=200)
    qualifications = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True, style={'base_template': 'textarea.html'})
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError({"email": "Email already exists."})
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError({"username": "Username already exists."})
        return value

    def validate(self, data):
        if data.get('user_type') == 'provider':
            required_provider_fields = ['specialization', 'address'] # Define required fields for provider registration
            missing = [f for f in required_provider_fields if not data.get(f)]
            if missing:
                raise serializers.ValidationError({f: ['This field is required for providers.'] for f in missing})
        return data

    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        phone_number = validated_data.pop('phone_number', None)
        provider_data = {}
        if user_type == 'provider':
            provider_keys = ['specialization', 'clinic_name', 'address', 'operating_hours', 'qualifications', 'bio', 'latitude', 'longitude']
            for key in provider_keys:
                if key in validated_data: provider_data[key] = validated_data.pop(key)

        try:
            user = User.objects.create_user(**validated_data) # Create base user
            user_profile = UserProfile.objects.create(user=user, user_type=user_type, phone_number=phone_number) # Create profile
            if user_type == 'provider':
                ProviderProfile.objects.create(profile=user_profile, **provider_data) # Create provider details
        except Exception as e:
            print(f"Error during user creation process: {e}")
            # Attempt cleanup if user was created but profiles failed
            if 'user' in locals() and user.pk:
                 user.delete()
            raise serializers.ValidationError("Failed to complete registration process.")

        return user

# --- Custom Token Serializer ---
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """ Customizes JWT claim and includes user details in login response. """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user); return token
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializer(self.user, context={'request': self.context.get('request')})
        data['user'] = serializer.data # Nest user details
        return data