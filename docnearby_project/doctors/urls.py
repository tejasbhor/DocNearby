# doctors/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
# Ensure the views are imported correctly from the SAME app's views.py
from .views import NearbyDoctorsView, DoctorProfileDetailView, MyDoctorProfileView
# If you have feedback URLs defined elsewhere, remove the import below
# from feedback.views import DoctorFeedbackListView

app_name = 'doctors' # Define app namespace

router = DefaultRouter()

urlpatterns = [
    # GET /api/doctors/nearby/?latitude=...&longitude=...&keywords=...
    path('doctors/nearby/', NearbyDoctorsView.as_view(), name='nearby_doctors'),

    # GET/PUT /api/doctors/profile/me/ (For logged-in doctor's own profile)
    path('doctors/profile/me/', MyDoctorProfileView.as_view(), name='my_doctor_profile'),

    # GET /api/doctors/{id}/ (For viewing any doctor's public profile)
    path('doctors/<int:pk>/', DoctorProfileDetailView.as_view(), name='doctor_detail'),

    # Optional: GET /api/doctors/{provider_pk}/feedback/ (If feedback list is handled here)
    # Make sure DoctorFeedbackListView is imported if this line is uncommented
    # path('doctors/<int:provider_pk>/feedback/', DoctorFeedbackListView.as_view(), name='doctor_feedback_list'),

    path('nearby/', NearbyDoctorsView.as_view(), name='nearby-doctors'),
]

urlpatterns += router.urls