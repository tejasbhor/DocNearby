# symptoms/urls.py
from django.urls import path
from .views import SymptomAnalysisView

app_name = 'symptoms'
urlpatterns = [
    # Path relative to the include() in the main urls.py (e.g., /api/symptoms/analyze/)
    path('symptoms/analyze/', SymptomAnalysisView.as_view(), name='symptom_analysis'),
]