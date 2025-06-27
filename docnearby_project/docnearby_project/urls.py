# docnearby_project/docnearby_project/urls.py
from django.contrib import admin
from django.urls import path, include # Ensure include is imported

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include Users URLs
    path('api/users/', include('users.urls', namespace='users_api')),

    # Include Symptoms URLs
    path('api/', include('symptoms.urls', namespace='symptoms_api')),

    # Include Doctors URLs
    path('api/', include('doctors.urls', namespace='doctors_api')),

    # Include Appointments URLs
    path('api/', include('appointments.urls', namespace='appointments_api')),

    # Include Feedback URLs (Make sure feedback/urls.py exists if uncommented)
    # path('api/', include('feedback.urls', namespace='feedback_api')),
]