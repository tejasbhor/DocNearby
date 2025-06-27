from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Appointment
from .serializers import AppointmentSerializer
from users.models import UserProfile, ProviderProfile

# Create your views here.

class AppointmentListView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_profile = self.request.user.userprofile
        if user_profile.user_type == 'patient':
            return Appointment.objects.filter(patient=user_profile)
        elif user_profile.user_type == 'provider':
            return Appointment.objects.filter(doctor=user_profile.providerprofile)
        return Appointment.objects.none()

    def perform_create(self, serializer):
        user_profile = self.request.user.userprofile
        if user_profile.user_type == 'patient':
            serializer.save(patient=user_profile)
        else:
            raise permissions.PermissionDenied("Only patients can create appointments")

class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_profile = self.request.user.userprofile
        if user_profile.user_type == 'patient':
            return Appointment.objects.filter(patient=user_profile)
        elif user_profile.user_type == 'provider':
            return Appointment.objects.filter(doctor=user_profile.providerprofile)
        return Appointment.objects.none()

    def perform_update(self, serializer):
        user_profile = self.request.user.userprofile
        appointment = self.get_object()

        # Only allow status updates for doctors
        if user_profile.user_type == 'provider':
            if 'status' in serializer.validated_data:
                new_status = serializer.validated_data['status']
                if new_status not in ['confirmed', 'cancelled', 'completed']:
                    raise permissions.PermissionDenied("Invalid status update")
                serializer.save()
            else:
                raise permissions.PermissionDenied("Doctors can only update appointment status")
        else:
            # Patients can only cancel their appointments
            if 'status' in serializer.validated_data:
                if serializer.validated_data['status'] != 'cancelled':
                    raise permissions.PermissionDenied("Patients can only cancel appointments")
            serializer.save()

class DoctorAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        doctor_id = self.kwargs.get('doctor_id')
        doctor = get_object_or_404(ProviderProfile, id=doctor_id)
        return Appointment.objects.filter(doctor=doctor)

class PatientAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        patient = get_object_or_404(UserProfile, id=patient_id)
        return Appointment.objects.filter(patient=patient)
