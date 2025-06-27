# doctors/views.py
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from users.models import ProviderProfile, UserProfile
from .serializers import DoctorListSerializer, DoctorDetailSerializer, MyDoctorProfileUpdateSerializer
from django.db.models import F, ExpressionWrapper, FloatField, Q, Value
from django.db.models.functions import Cos, Sin, Radians, Power, Sqrt, ACos
from django.conf import settings
import math
import time
from rest_framework.views import APIView
from .models import Doctor
import requests
import os
import google.generativeai as genai
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor
import re

# Initialize Gemini API
if hasattr(settings, 'GOOGLE_API_KEY'):
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    print("Warning: GOOGLE_API_KEY not found in settings. Gemini API features will be disabled.")
    model = None

# Haversine distance calculation function
def calculate_haversine(lat1, lon1, lat2, lon2):
    """ Calculates distance between two lat/lon points in kilometers. """
    if None in [lat1, lon1, lat2, lon2]: return float('inf') # Return infinity for invalid coords
    R = 6371.0  # Earth radius in kilometers
    try:
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        a = max(0, min(a, 1.0)) # Ensure value is valid for asin
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c
        return distance
    except (ValueError, TypeError) as e: # Catch potential math errors
        print(f"Error calculating Haversine for ({lat1},{lon1}) to ({lat2},{lon2}): {e}")
        return float('inf') # Return infinity on math error

def fetch_web_results(latitude, longitude, radius, specialty=''):
    """Fetch doctor information from web sources"""
    try:
        # List of web sources to scrape
        sources = [
            {
                'name': 'practo',
                'url': f'https://www.practo.com/search/doctors?results_type=doctor&q={specialty}&lat={latitude}&lng={longitude}&radius={radius}',
                'parser': parse_practo_results
            },
            {
                'name': 'lybrate',
                'url': f'https://www.lybrate.com/search/doctors?q={specialty}&lat={latitude}&lng={longitude}&radius={radius}',
                'parser': parse_lybrate_results
            }
        ]

        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for source in sources:
                futures.append(executor.submit(fetch_from_source, source, latitude, longitude, radius, specialty))
            
            for future in futures:
                try:
                    source_results = future.result()
                    results.extend(source_results)
                except Exception as e:
                    print(f"Error fetching from source: {str(e)}")

        return results
    except Exception as e:
        print(f"Error in web scraping: {str(e)}")
        return []

def fetch_from_source(source, latitude, longitude, radius, specialty):
    """Fetch and parse results from a single source"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(source['url'], headers=headers, timeout=10)
        response.raise_for_status()
        return source['parser'](response.text, latitude, longitude)
    except Exception as e:
        print(f"Error fetching from {source['name']}: {str(e)}")
        return []

def parse_practo_results(html, latitude, longitude):
    """Parse results from Practo"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        doctors = []
        
        for card in soup.select('.doctor-card'):
            try:
                name = card.select_one('.doctor-name').text.strip()
                specialty = card.select_one('.specialization').text.strip()
                address = card.select_one('.clinic-address').text.strip()
                rating = float(card.select_one('.rating-value').text.strip())
                
                # Extract coordinates from data attributes or map link
                lat = float(card.get('data-lat', latitude))
                lng = float(card.get('data-lng', longitude))
                
                doctors.append({
                    'name': name,
                    'specialty': specialty,
                    'address': address,
                    'rating': rating,
                    'latitude': lat,
                    'longitude': lng,
                    'source': 'practo',
                    'is_verified': False
                })
            except Exception as e:
                print(f"Error parsing Practo doctor card: {str(e)}")
                continue
                
        return doctors
    except Exception as e:
        print(f"Error parsing Practo results: {str(e)}")
        return []

def parse_lybrate_results(html, latitude, longitude):
    """Parse results from Lybrate"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        doctors = []
        
        for card in soup.select('.doctor-card'):
            try:
                name = card.select_one('.doctor-name').text.strip()
                specialty = card.select_one('.specialization').text.strip()
                address = card.select_one('.clinic-address').text.strip()
                rating = float(card.select_one('.rating-value').text.strip())
                
                # Extract coordinates from data attributes or map link
                lat = float(card.get('data-lat', latitude))
                lng = float(card.get('data-lng', longitude))
                
                doctors.append({
                    'name': name,
                    'specialty': specialty,
                    'address': address,
                    'rating': rating,
                    'latitude': lat,
                    'longitude': lng,
                    'source': 'lybrate',
                    'is_verified': False
                })
            except Exception as e:
                print(f"Error parsing Lybrate doctor card: {str(e)}")
                continue
                
        return doctors
    except Exception as e:
        print(f"Error parsing Lybrate results: {str(e)}")
        return []

class NearbyDoctorsView(APIView):
    def get(self, request):
        try:
            latitude = float(request.query_params.get('latitude'))
            longitude = float(request.query_params.get('longitude'))
            specialty = request.query_params.get('specialty', '')
            symptoms = request.query_params.get('symptoms', '')
            include_web_results = request.query_params.get('include_web_results', 'true').lower() == 'true'

            # Query verified doctors from database
            doctors = Doctor.objects.filter(is_verified=True)

            # Filter by specialty if provided
            if specialty:
                doctors = doctors.filter(specialty__icontains=specialty)

            # Calculate distance for each doctor
            nearby_doctors = []
            for doctor in doctors:
                if doctor.latitude is not None and doctor.longitude is not None:
                    try:
                        distance = calculate_haversine(
                            latitude, longitude,
                            float(doctor.latitude),
                            float(doctor.longitude)
                        )
                        doctor.distance = distance
                        doctor.source = 'platform'
                        doctor.is_verified = True
                        nearby_doctors.append(doctor)
                    except (ValueError, TypeError) as e:
                        print(f"Error calculating distance for doctor {doctor.id}: {str(e)}")
                        continue

            # Sort by distance
            nearby_doctors.sort(key=lambda x: x.distance)

            # Fetch Google Places results if requested
            google_places_doctors = []
            if include_web_results:
                try:
                    google_places_doctors = self.fetch_google_places(latitude, longitude, specialty)
                except Exception as e:
                    print(f"Error fetching Google Places results: {str(e)}")

            # Combine and sort all results
            all_doctors = nearby_doctors + google_places_doctors
            all_doctors.sort(key=lambda x: x.distance if hasattr(x, 'distance') else float('inf'))

            # Serialize the results
            serializer = DoctorListSerializer(all_doctors, many=True)
            
            # If no doctors found, return a helpful message
            if not all_doctors:
                return Response({
                    'message': 'No doctors found in your area. Try adjusting your search criteria or expanding your search radius.',
                    'results': []
                }, status=status.HTTP_200_OK)

            return Response({
                'results': serializer.data,
                'count': len(all_doctors),
                'verified_count': len(nearby_doctors),
                'google_count': len(google_places_doctors),
                'message': f'Found {len(all_doctors)} healthcare providers near you'
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({
                'error': 'Invalid latitude or longitude provided',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error in NearbyDoctorsView: {str(e)}")
            return Response({
                'error': 'An error occurred while fetching doctors',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def fetch_google_places(self, latitude, longitude, specialty=''):
        """Fetch healthcare providers from Google Places API"""
        try:
            # Use Google Places API to find healthcare providers
            url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
            params = {
                'location': f'{latitude},{longitude}',
                'radius': 10000,  # 10km radius
                'type': 'doctor|hospital|health',
                'keyword': specialty if specialty else 'healthcare',
                'key': settings.GOOGLE_MAPS_API_KEY
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data['status'] != 'OK':
                print(f"Google Places API error: {data['status']}")
                return []

            places = []
            for place in data['results']:
                try:
                    # Get place details for more information
                    details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
                    details_params = {
                        'place_id': place['place_id'],
                        'fields': 'name,formatted_address,formatted_phone_number,rating,types,website',
                        'key': settings.GOOGLE_MAPS_API_KEY
                    }
                    
                    details_response = requests.get(details_url, params=details_params)
                    details_response.raise_for_status()
                    details = details_response.json()['result']

                    # Create a doctor-like object
                    doctor = {
                        'name': place['name'],
                        'address': place.get('vicinity', details.get('formatted_address', '')),
                        'latitude': place['geometry']['location']['lat'],
                        'longitude': place['geometry']['location']['lng'],
                        'rating': place.get('rating', 0),
                        'phone': details.get('formatted_phone_number', ''),
                        'website': details.get('website', ''),
                        'types': place.get('types', []),
                        'source': 'google_places',
                        'is_verified': False,
                        'distance': calculate_haversine(
                            latitude, longitude,
                            place['geometry']['location']['lat'],
                            place['geometry']['location']['lng']
                        )
                    }
                    places.append(doctor)
                except Exception as e:
                    print(f"Error processing Google Place: {str(e)}")
                    continue

            return places
        except Exception as e:
            print(f"Error fetching Google Places: {str(e)}")
            return []

    def rank_doctors_by_symptoms(self, doctors, symptoms):
        try:
            # Prepare the prompt for Gemini
            prompt = f"""
            Rank these doctors based on their relevance to the following symptoms: {', '.join(symptoms)}
            For each doctor, consider their specialty, experience, and any other relevant information.
            Return the doctors in order of most relevant to least relevant.
            Doctors: {[f"{d.name} ({d.specialty})" for d in doctors]}
            """

            # Get ranking from Gemini
            response = self.gemini_model.generate_content(prompt)
            ranked_names = [name.strip() for name in response.text.split('\n') if name.strip()]

            # Reorder doctors based on Gemini's ranking
            ranked_doctors = []
            for name in ranked_names:
                for doctor in doctors:
                    if doctor.name in name:
                        ranked_doctors.append(doctor)
                        break

            # Add any remaining doctors that weren't ranked
            for doctor in doctors:
                if doctor not in ranked_doctors:
                    ranked_doctors.append(doctor)

            return ranked_doctors
        except Exception as e:
            print(f"Error in Gemini ranking: {str(e)}")
            return doctors  # Return original order if ranking fails

class DoctorProfileDetailView(APIView):
    def get(self, request, pk):
        try:
            doctor = Doctor.objects.get(pk=pk)
            serializer = DoctorDetailSerializer(doctor)
            return Response(serializer.data)
        except Doctor.DoesNotExist:
            return Response(
                {'error': 'Doctor not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class MyDoctorProfileView(APIView):
    def get(self, request):
        try:
            doctor = Doctor.objects.get(user=request.user)
            serializer = DoctorDetailSerializer(doctor)
            return Response(serializer.data)
        except Doctor.DoesNotExist:
            return Response(
                {'error': 'Doctor profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )