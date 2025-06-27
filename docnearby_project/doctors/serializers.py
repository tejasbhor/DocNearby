# doctors/serializers.py
from rest_framework import serializers
# --- Import models from the 'users' app ---
from users.models import ProviderProfile, UserProfile
# --- Import the standard User model correctly ---
from django.contrib.auth.models import User # <--- CORRECT IMPORT FOR USER MODEL
from .models import Doctor

# Serializer for displaying doctor info in lists (e.g., nearby search results)
class DoctorListSerializer(serializers.ModelSerializer):
    """ Serializer for listing providers, including calculated distance and source. """
    # Include fields from related User and UserProfile models via source
    name = serializers.SerializerMethodField(read_only=True)
    # Use 'role' for consistency with other serializers, mapping from user_type
    role = serializers.CharField(source='profile.user_type', read_only=True)
    phone_number = serializers.CharField(source='profile.phone_number', read_only=True, allow_null=True) # Allow null

    # Fields added dynamically by the view (distance, source) - mark as read-only
    distance = serializers.FloatField(read_only=True, required=False, allow_null=True) # Allow null
    source = serializers.CharField(read_only=True, required=False, default='platform')

    class Meta:
        model = ProviderProfile # Based on the ProviderProfile model
        fields = [
            'id',           # ProviderProfile primary key
            'name',         # Calculated full name
            'specialization',
            'address',
            'latitude',
            'longitude',
            'is_verified',
            'role',         # Mapped from user_type
            'phone_number',
            'distance',     # Added by view
            'source',       # Added by view (distinguishes platform vs google)
            'clinic_name',  # Optional: include if useful in list view
        ]
        # All fields are effectively read-only in this list context
        read_only_fields = fields

    def get_name(self, obj):
        """ Gets the full name from the related User model. """
        # obj here is a ProviderProfile instance
        # Navigate through the relationships: ProviderProfile -> UserProfile -> User
        try:
            user = obj.profile.user
            fname = user.first_name
            lname = user.last_name
            # Return combined name or fallback to username
            return f"{fname} {lname}".strip() or user.username
        except (UserProfile.DoesNotExist, User.DoesNotExist, AttributeError):
             # Handle cases where related objects might be missing unexpectedly
             return "Unknown Doctor"


# Serializer for the detailed public doctor profile view (/api/doctors/{id}/)
class DoctorDetailSerializer(serializers.ModelSerializer):
    """ Serializer for the detailed public view of a provider. """
    # Get related User fields via the profile link
    name = serializers.SerializerMethodField(read_only=True)
    phone_number = serializers.CharField(source='profile.phone_number', read_only=True, allow_null=True)
    email = serializers.EmailField(source='profile.user.email', read_only=True) # Get email from User

    class Meta:
        model = ProviderProfile
        # Include all relevant public fields from ProviderProfile model
        fields = [
            'id', # ProviderProfile primary key
            'name',
            'email',
            'phone_number',
            'specialization',
            'clinic_name',
            'address',
            'latitude',
            'longitude',
            'operating_hours',
            'is_verified',
            'qualifications',
            'bio',
            # Do NOT include 'profile' FK object itself unless specifically needed by frontend
        ]
        # All fields are read-only for the public detail view
        read_only_fields = fields

    def get_name(self, obj):
        """ Gets the full name from the related User model. """
        try:
            user = obj.profile.user
            fname = user.first_name
            lname = user.last_name
            return f"{fname} {lname}".strip() or user.username
        except (UserProfile.DoesNotExist, User.DoesNotExist, AttributeError):
             return "Unknown Doctor"

# Serializer for Doctors updating their OWN profile (/api/doctors/profile/me/)
class MyDoctorProfileUpdateSerializer(serializers.ModelSerializer):
    """ Serializer for allowing authenticated providers to update their profile fields. """
    # Define fields that can be updated. Make required fields explicit here.
    # Backend validation ensures these are provided on PUT/PATCH if required=True.
    specialization = serializers.CharField(required=True, allow_blank=False, max_length=100)
    address = serializers.CharField(required=True, allow_blank=False, style={'base_template': 'textarea.html'})
    clinic_name = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=150)
    operating_hours = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=200)
    qualifications = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True, style={'base_template': 'textarea.html'})
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    # If allowing phone number update via this endpoint (needs custom update logic):
    # phone_number = serializers.CharField(source='profile.phone_number', required=False, allow_blank=True, max_length=20)

    class Meta:
        model = ProviderProfile
        # List ONLY the fields from ProviderProfile that the doctor can EDIT
        # Ensure these field names match the actual fields in the ProviderProfile model
        fields = [
            'specialization', 'clinic_name', 'address', 'latitude',
            'longitude', 'operating_hours', 'qualifications', 'bio',
            # Add 'phone_number' here ONLY if implementing custom update logic below
        ]
        # Excluded by default: 'id', 'profile' (linked automatically), 'is_verified' (admin only)

    # --- Optional: Custom update method if updating related UserProfile fields ---
    # def update(self, instance, validated_data):
    #     # Example: Handling nested UserProfile update for phone_number
    #     profile_data = validated_data.pop('profile', {}) # Assuming phone_number was nested under 'profile' key
    #     phone_number = profile_data.get('phone_number', None) # Or get directly if not nested source

    #     # Update ProviderProfile fields using default ModelSerializer logic
    #     instance = super().update(instance, validated_data)

    #     # Update related UserProfile field if phone_number data was provided
    #     if phone_number is not None:
    #         user_profile = instance.profile
    #         user_profile.phone_number = phone_number
    #         user_profile.save(update_fields=['phone_number'])
    #         print(f"Updated phone number for {user_profile.user.username}")

    #     return instance
    # --- End Optional Update ---

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            'id',
            'name',
            'specialty',
            'experience',
            'rating',
            'reviews',
            'address',
            'phone_number',
            'email',
            'latitude',
            'longitude',
            'license_number',
            'consultation_fee',
            'is_available',
            'is_verified',
            'clinic_name',
            'qualifications',
            'bio',
            'profile_image',
            'operating_hours',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class DoctorListSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(read_only=True)
    source = serializers.CharField(read_only=True, default='platform')

    class Meta:
        model = Doctor
        fields = [
            'id',
            'name',
            'specialty',
            'experience',
            'rating',
            'reviews',
            'address',
            'phone_number',
            'latitude',
            'longitude',
            'is_available',
            'is_verified',
            'clinic_name',
            'distance',
            'source'
        ]

class DoctorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            'id',
            'name',
            'specialty',
            'experience',
            'rating',
            'reviews',
            'address',
            'phone_number',
            'email',
            'latitude',
            'longitude',
            'license_number',
            'consultation_fee',
            'is_available',
            'is_verified',
            'clinic_name',
            'qualifications',
            'bio',
            'profile_image',
            'operating_hours',
            'created_at',
            'updated_at'
        ]

class MyDoctorProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            'name',
            'specialty',
            'experience',
            'address',
            'phone_number',
            'email',
            'latitude',
            'longitude',
            'license_number',
            'consultation_fee',
            'is_available',
            'clinic_name',
            'qualifications',
            'bio',
            'profile_image',
            'operating_hours'
        ]