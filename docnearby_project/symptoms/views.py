# symptoms/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import SymptomInputSerializer # Assuming this is in symptoms/serializers.py
import google.generativeai as genai
from django.conf import settings
import json # To parse potential JSON output from Gemini
import re # For cleaning potential markdown fences

# --- Gemini Configuration ---
gemini_model = None
if settings.GOOGLE_API_KEY:
    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        # Using flash for potentially faster/cheaper responses in hackathon
        gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print("Gemini API client configured successfully (symptoms app).")
    except Exception as e:
        print(f"!!! ERROR configuring Gemini API client: {e}")
else:
    # This case is handled by the check within the view now
    print("!!! WARNING: Gemini API Key missing, AI features disabled.")

# Define safety settings (adjust thresholds if needed, BLOCK_NONE can be risky)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    # Be cautious with DANGEROUS_CONTENT for medical topics, may need BLOCK_NONE
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# --- Prompt for Gemini ---
# This prompt guides the LLM to output the specific JSON structure needed.
GEMINI_PROMPT_TEMPLATE = """
Analyze the following patient symptoms and provide potential related medical conditions
and relevant medical specialties or keywords to search for nearby healthcare providers.

Symptoms List:
{symptom_list}

Instructions:
1. List 2-3 potential medical conditions or issues these symptoms might indicate. 
   - Use clear, non-alarming language
   - Avoid medical jargon
   - Focus on common conditions first
   - Example: "Common Cold or Flu", "Muscle Strain", "Mild Allergic Reaction"

2. Generate a list of 3-5 relevant healthcare providers to consult, ordered by priority:
   - Start with most appropriate specialist
   - Include general practitioners when appropriate
   - Add urgent care/emergency if symptoms are severe
   - Example: ["Primary Care Doctor", "Allergist", "Urgent Care"]

3. Provide a brief, reassuring summary that:
   - Acknowledges the symptoms
   - Suggests next steps
   - Emphasizes the importance of professional consultation
   - Uses a calm, supportive tone

Output the result ONLY as a valid JSON object with the following exact keys:
- "potential_conditions": ["Condition 1", "Condition 2", ...] (list of strings)
- "recommended_providers": ["Provider 1", "Provider 2", ...] (list of strings)
- "summary": "Brief, reassuring summary." (string)
- "urgency_level": "low" | "medium" | "high" (string)

Example Output for "skin rash, itching":
{{
  "potential_conditions": ["Mild Allergic Reaction", "Contact Dermatitis"],
  "recommended_providers": ["Primary Care Doctor", "Allergist", "Dermatologist"],
  "summary": "These symptoms suggest a mild skin reaction. While not urgent, seeing a doctor can help identify the cause and provide relief.",
  "urgency_level": "low"
}}

Now analyze the provided symptoms.

JSON Output:
"""
# --- End Prompt ---

class SymptomAnalysisView(APIView):
    """
    Uses Gemini API to analyze symptoms and suggest conditions & search keywords.
    Requires user authentication.
    """
    permission_classes = [permissions.IsAuthenticated] # User must be logged in

    def post(self, request, *args, **kwargs):
        # Check if Gemini client was configured successfully
        if not gemini_model:
            return Response({"error": "AI analysis service not available due to configuration error."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Validate incoming data using the serializer
        serializer = SymptomInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Prepare prompt input
        symptoms = serializer.validated_data['symptoms']
        symptom_list_str = "- " + "\n- ".join(symptoms) # Format list for prompt
        prompt = GEMINI_PROMPT_TEMPLATE.format(symptom_list=symptom_list_str)
        print(f"[Gemini Analysis] Analyzing symptoms: {', '.join(symptoms)}")

        try:
            # --- Call Gemini API ---
            print("[Gemini Analysis] Calling Gemini API...")
            generation_config = genai.types.GenerationConfig(
                # candidate_count=1, # Default
                # max_output_tokens=250, # Limit token usage
                temperature=0.4 # Lower temperature for more focused, less creative output
            )
            response = gemini_model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            # --- End Gemini API Call ---

            print("[Gemini Analysis] Gemini response received.")

            # --- Process Gemini Response ---
            try:
                 # Check for safety blocks first
                if not response.candidates:
                    block_reason = "Unknown"
                    try: block_reason = response.prompt_feedback.block_reason
                    except Exception: pass
                    print(f"[Gemini Analysis] Blocked by safety settings: {block_reason}")
                    # It's better to return a structured error than the block reason directly
                    return Response({"error": "Analysis could not be completed due to content restrictions."}, status=status.HTTP_400_BAD_REQUEST)

                raw_text = response.text.strip()
                print(f"[Gemini Analysis] Raw response text:\n{raw_text}")

                # Clean potential markdown JSON fences (```json ... ```)
                json_string = re.sub(r"```json\s*(.*?)\s*```", r"\1", raw_text, flags=re.DOTALL | re.IGNORECASE)
                json_string = json_string.strip() # Remove leading/trailing whitespace

                # Attempt to parse the JSON
                parsed_data = json.loads(json_string)

                # Validate expected structure
                if not all(k in parsed_data for k in ["potential_conditions", "recommended_providers", "summary", "urgency_level"]) or \
                   not isinstance(parsed_data.get("potential_conditions"), list) or \
                   not isinstance(parsed_data.get("recommended_providers"), list) or \
                   not isinstance(parsed_data.get("summary"), str) or \
                   not isinstance(parsed_data.get("urgency_level"), str):
                     raise ValueError("Gemini response missing required JSON keys or has incorrect types.")

                # Add standard disclaimer
                parsed_data["disclaimer"] = "AI analysis is informational only. Always consult a qualified healthcare professional for diagnosis and treatment."

                print(f"[Gemini Analysis] Parsed Data: {parsed_data}")
                return Response(parsed_data, status=status.HTTP_200_OK)

            except (json.JSONDecodeError, ValueError) as json_e:
                 print(f"Error parsing Gemini JSON response: {json_e}")
                 print(f"Raw text was: {raw_text}")
                 # Return error indicating format issue from AI
                 return Response({
                     "error": "AI analysis result could not be processed.",
                     "raw_ai_response": raw_text # Optional: Send raw response for debugging on frontend
                 }, status=status.HTTP_502_BAD_GATEWAY) # Bad Gateway indicates issue with upstream service (Gemini)
            # --- End Process Response ---

        except Exception as e:
            # Catch potential API errors during the call itself
            print(f"[Gemini Analysis] Error calling Gemini API: {type(e).__name__} - {e}")
            error_detail = getattr(e, 'message', str(e))
            return Response({"error": f"AI analysis service failed: {error_detail}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)