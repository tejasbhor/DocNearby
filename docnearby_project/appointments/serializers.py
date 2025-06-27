from rest_framework import serializers
from .models import Appointment
from users.serializers import UserProfileSerializer, ProviderProfileSerializer
from users.models import UserProfile, ProviderProfile

class AppointmentSerializer(serializers.ModelSerializer):
    patient = UserProfileSerializer(read_only=True)
    doctor = ProviderProfileSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.filter(user_type='patient'),
        write_only=True,
        source='patient'
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=ProviderProfile.objects.all(),
        write_only=True,
        source='doctor'
    )

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'doctor', 'patient_id', 'doctor_id',
            'date', 'time', 'status', 'symptoms', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']

    def validate(self, data):
        # Check if the appointment time is in the future
        from datetime import datetime, date
        if data['date'] < date.today():
            raise serializers.ValidationError("Appointment date cannot be in the past")
        
        if data['date'] == date.today() and data['time'] < datetime.now().time():
            raise serializers.ValidationError("Appointment time cannot be in the past")

        # Check for overlapping appointments
        existing_appointments = Appointment.objects.filter(
            doctor=data['doctor'],
            date=data['date'],
            time=data['time'],
            status__in=['pending', 'confirmed']
        )
        if existing_appointments.exists():
            raise serializers.ValidationError("This time slot is already booked")

        return data 