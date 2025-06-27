# symptoms/models.py
from django.db import models
# If UserProfile is in 'users' app:
# from users.models import UserProfile

# --- Model to potentially store known symptoms (Optional) ---
# class Symptom(models.Model):
#     name = models.CharField(max_length=150, unique=True)
#     description = models.TextField(blank=True, null=True)
#
#     def __str__(self):
#         return self.name

# --- Model to log user searches (Optional but useful) ---
# class PatientSymptomLog(models.Model):
#     # Ensure UserProfile is imported correctly if using FK
#     # patient_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='symptom_logs', limit_choices_to={'user_type': 'patient'})
#     symptoms_text = models.TextField(help_text="Comma-separated or free text symptoms entered by user")
#     # symptoms = models.ManyToManyField(Symptom, blank=True) # If using Symptom model
#     predicted_condition = models.CharField(max_length=255, blank=True, null=True, help_text="Result from AI analysis")
#     timestamp = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         # Use patient_profile relation if defined
#         # return f"Log for {self.patient_profile.user.username} at {self.timestamp}"
#         return f"Symptom log at {self.timestamp}"