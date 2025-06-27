from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile', null=True, blank=True)
    name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=255)
    experience = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    reviews = models.IntegerField(default=0)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    license_number = models.CharField(max_length=50, null=True, blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    clinic_name = models.CharField(max_length=255, null=True, blank=True)
    qualifications = models.TextField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_image = models.URLField(null=True, blank=True)
    operating_hours = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating', '-experience']

    def __str__(self):
        return f"{self.name} - {self.specialty}"
