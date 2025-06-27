from django.urls import path
from .views import (
    AppointmentListView,
    AppointmentDetailView,
    DoctorAppointmentsView,
    PatientAppointmentsView
)

app_name = 'appointments'

urlpatterns = [
    # List and create appointments
    path('appointments/', AppointmentListView.as_view(), name='appointment_list'),
    
    # Get, update, or delete specific appointment
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment_detail'),
    
    # Get all appointments for a specific doctor
    path('doctors/<int:doctor_id>/appointments/', DoctorAppointmentsView.as_view(), name='doctor_appointments'),
    
    # Get all appointments for a specific patient
    path('patients/<int:patient_id>/appointments/', PatientAppointmentsView.as_view(), name='patient_appointments'),
] 