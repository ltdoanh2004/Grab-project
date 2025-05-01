#!/usr/bin/env python3
"""
Test script for the Trip Plan API endpoint
"""
import requests
import json
import sys

# API endpoint
API_URL = "http://localhost:8000/api/v1/trip/get_plan"

# Sample test data
test_data = {
  "accommodation": {
    "accommodations": [
      {
        "accommodation_id": "hotel123",
        "booking_link": "https://example.com/booking",
        "city": "Đà Nẵng",
        "description": "A luxury beachfront hotel with stunning views",
        "destination_id": "danang001",
        "elderly_friendly": True,
        "image_url": [
          {
            "alt": "Hotel exterior",
            "url": "https://example.com/hotel1.jpg"
          }
        ],
        "location": "Mỹ Khê Beach, Đà Nẵng",
        "name": "Beach Resort Đà Nẵng",
        "price": 1500000,
        "rating": 4.7,
        "room_info": "Spacious rooms with ocean view",
        "room_types": [
          {
            "bed_type": "King",
            "conditions": "Free cancellation",
            "name": "Deluxe Ocean View",
            "occupancy": "2 adults",
            "price": "1,500,000 VND",
            "tax_and_fee": "150,000 VND"
          }
        ],
        "tax_info": "10% VAT included",
        "unit": "VND"
      }
    ]
  },
  "places": {
    "places": [
      {
        "address": "Thọ Quang, Sơn Trà, Đà Nẵng",
        "categories": "Nature,Landmark",
        "description": "Stunning peninsula with amazing views of the coastline",
        "destination_id": "danang001",
        "duration": "3 hours",
        "images": [
          {
            "alt": "Son Tra Peninsula view",
            "url": "https://example.com/sontra.jpg"
          }
        ],
        "main_image": "https://example.com/sontra_main.jpg",
        "name": "Bán Đảo Sơn Trà",
        "opening_hours": "Open 24 hours",
        "place_id": "place001",
        "price": "Free",
        "rating": 4.8,
        "reviews": [
          "Beautiful natural scenery, perfect for photography"
        ],
        "type": "Nature",
        "url": "https://example.com/sontra"
      },
      {
        "address": "Hòa Hiệp Nam, Liên Chiểu, Đà Nẵng",
        "categories": "Culture,Religious",
        "description": "Ancient marble mountains with caves, tunnels, and Buddhist sanctuaries",
        "destination_id": "danang001",
        "duration": "2 hours",
        "images": [
          {
            "alt": "Marble Mountains view",
            "url": "https://example.com/marblemont.jpg"
          }
        ],
        "main_image": "https://example.com/marblemont_main.jpg",
        "name": "Ngũ Hành Sơn",
        "opening_hours": "7:00 - 17:30",
        "place_id": "place002",
        "price": "40,000 VND",
        "rating": 4.6,
        "reviews": [
          "Amazing views from the top, worth the climb"
        ],
        "type": "Landmark",
        "url": "https://example.com/marblemont"
      },
      {
        "address": "Bãi biển Mỹ Khê, Đà Nẵng",
        "categories": "Beach,Relaxation",
        "description": "One of the most beautiful beaches in Vietnam with white sand",
        "destination_id": "danang001",
        "duration": "Half day",
        "images": [
          {
            "alt": "My Khe Beach",
            "url": "https://example.com/mykhe.jpg"
          }
        ],
        "main_image": "https://example.com/mykhe_main.jpg",
        "name": "Bãi biển Mỹ Khê",
        "opening_hours": "Open 24 hours",
        "place_id": "place003",
        "price": "Free",
        "rating": 4.9,
        "reviews": [
          "Perfect beach with clean water and beautiful sand"
        ],
        "type": "Beach",
        "url": "https://example.com/mykhe"
      }
    ]
  },
  "restaurants": {
    "restaurants": [
      {
        "address": "K123/45 Lê Lợi, Đà Nẵng",
        "cuisines": "Vietnamese, Seafood",
        "description": "Local restaurant famous for its fresh seafood",
        "destination_id": "danang001",
        "example_reviews": "The seafood is incredibly fresh",
        "is_booking": True,
        "is_delivery": False,
        "is_opening": True,
        "location": {
          "lat": 16.0544,
          "lon": 108.2232
        },
        "main_image": "https://example.com/restaurant1.jpg",
        "media_urls": "https://example.com/rest1_media",
        "name": "Hải Sản Đà Nẵng",
        "num_reviews": 120,
        "opening_hours": "11:00 - 22:00",
        "phone": "+84 123 456 789",
        "photo_url": "https://example.com/rest1_photos",
        "price_range": "$$",
        "rating": 4.5,
        "restaurant_id": "rest001",
        "review_summary": "Excellent seafood, great service",
        "reviews": [
          "Amazing food, must try the grilled fish!"
        ],
        "services": [
          "Dine-in",
          "Takeaway"
        ],
        "url": "https://example.com/restaurant1"
      },
      {
        "address": "56 Bạch Đằng, Đà Nẵng",
        "cuisines": "Vietnamese, Asian Fusion",
        "description": "Riverside restaurant with traditional Vietnamese cuisine",
        "destination_id": "danang001",
        "example_reviews": "Great river view while dining",
        "is_booking": True,
        "is_delivery": True,
        "is_opening": True,
        "location": {
          "lat": 16.0712,
          "lon": 108.2242
        },
        "main_image": "https://example.com/restaurant2.jpg",
        "media_urls": "https://example.com/rest2_media",
        "name": "Sông Hàn Restaurant",
        "num_reviews": 95,
        "opening_hours": "10:00 - 22:30",
        "phone": "+84 123 987 654",
        "photo_url": "https://example.com/rest2_photos",
        "price_range": "$$$",
        "rating": 4.6,
        "restaurant_id": "rest002",
        "review_summary": "Beautiful view, authentic food",
        "reviews": [
          "The banh xeo is incredible here!"
        ],
        "services": [
          "Dine-in",
          "Takeaway",
          "Delivery"
        ],
        "url": "https://example.com/restaurant2"
      }
    ]
  }
}

def test_trip_plan_api():
    """Test the trip plan API endpoint"""
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        # Send POST request to the API
        response = requests.post(API_URL, json=test_data, headers=headers)
        
        # Print response status code
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Parse and pretty print the JSON response
            result = response.json()
            print("\nAPI Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Check if the response contains a trip plan
            if result.get("status") == "success" and result.get("plan"):
                print("\n✅ Test passed: Trip plan generated successfully")
                
                # Print summary information
                summary = result["plan"]["summary"]
                print(f"\nTrip Summary:")
                print(f"- Duration: {summary['total_duration']}")
                print(f"- Total Cost: {summary['total_cost']} VND")
                print(f"- Accommodations: {summary['accommodations']}")
                print(f"- Places: {summary['places']}")
                print(f"- Restaurants: {summary['restaurants']}")
                
                # Print number of days in the itinerary
                print(f"\nItinerary contains {len(result['plan']['itinerary'])} day(s)")
            else:
                print(f"\n❌ Test failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"\n❌ Test failed: HTTP Error {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")

if __name__ == "__main__":
    print("Testing Trip Plan API...")
    test_trip_plan_api() 