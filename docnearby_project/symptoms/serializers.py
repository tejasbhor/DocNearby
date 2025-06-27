# symptoms/serializers.py
from rest_framework import serializers

class SymptomInputSerializer(serializers.Serializer):
    """ Serializer to validate the list of symptoms coming from the frontend. """
    symptoms = serializers.ListField(
       child=serializers.CharField(max_length=150, allow_blank=False, trim_whitespace=True), # Trim whitespace
       min_length=1,
       help_text="List of symptom strings provided by the user."
    )

class SymptomAnalysisResultSerializer(serializers.Serializer):
    """ Serializer to define the structure of the data returned BY the analysis view. """
    # Adjust field names and types based on what your AI model/view will actually output
    predicted_conditions = serializers.ListField(child=serializers.CharField(), read_only=True)
    # Example: confidence might be a float or string depending on output format
    confidence = serializers.CharField(read_only=True, allow_null=True, required=False)
    # Add any other fields the AI might return
    # additional_info = serializers.CharField(read_only=True, required=False)