# docnearby_project/users/models.py
from django.db import models
from django.conf import settings # Use settings to reference the User model

class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('patient', 'Patient'),
        ('provider', 'Provider'), # Use 'provider' key for doctors
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile' # Allows accessing profile from user: user.profile
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    # Add other common fields if needed (e.g., date_of_birth)

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

class ProviderProfile(models.Model):
    # Link to the UserProfile, ensuring it's a 'provider' type
    profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='provider_details', # Allows accessing provider details from profile: profile.provider_details
        limit_choices_to={'user_type': 'provider'}
    )
    # Provider specific fields
    specialization = models.CharField(max_length=100, blank=True, null=True)
    clinic_name = models.CharField(max_length=150, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    operating_hours = models.CharField(max_length=200, blank=True, null=True)
    is_verified = models.BooleanField(default=False) # Admin controlled verification
    qualifications = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    # Add license_number if required
    # license_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Provider: {self.profile.user.username} ({self.specialization or 'N/A'})"

