import googlemaps
import time
import json
import os
import logging
from datetime import datetime
from google import genai
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('elderly_friendly.log'),
        logging.StreamHandler()
    ]
)

# API Keys
PLACES_API_KEY = 'AIzaSyBPRDc8Sp3M_tlv0VYZOW2WIA6SCbBHYWM'
GEMINI_API_KEY = 'AIzaSyDw7pATXuPed2F_fHyi0JtwRmsvxmGVPBM'

# Initialize Google Maps client
gmaps = googlemaps.Client(key=PLACES_API_KEY)

client = genai.Client(api_key=GEMINI_API_KEY)

# Keywords to check for elderly-friendly features
ELDERLY_KEYWORDS = [
    'elderly', 'senior', 'old people', 'accessible', 'wheelchair', 
    'no stairs', 'elevator', 'lift', 'ramp', 'handrail', 
    'người già', 'người cao tuổi', 'người lớn tuổi', 'xe lăn', 
    'thang máy', 'không cầu thang', 'dốc', 'tay vịn'
]

def analyze_review_text(text):
    """
    Analyze review text using Gemini to detect elderly-friendly mentions
    """
    try:
        prompt = f"""
        Analyze this review text and determine if it mentions anything about elderly-friendly features or accessibility.
        Focus on aspects like wheelchair access, elevators, ramps, handrails, or any mentions of elderly/senior accommodations.
        
        Review text: {text}
        
        Please provide:
        1. A sentiment score (-1 to 1, where -1 is negative, 0 is neutral, 1 is positive)
        2. A list of elderly-friendly features mentioned
        3. A brief explanation of why this place might be suitable for elderly people
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        response_text = response.text
        
        # Extract sentiment score
        sentiment_match = re.search(r'sentiment score:?\s*([-]?\d+\.?\d*)', response_text.lower())
        sentiment_score = float(sentiment_match.group(1)) if sentiment_match else 0.0
        
        # Extract elderly-friendly features
        features = []
        for keyword in ELDERLY_KEYWORDS:
            if keyword in text.lower():
                features.append(keyword)
        
        return {
            'sentiment_score': sentiment_score,
            'elderly_keywords': features,
            'analysis': response_text
        }
    except Exception as e:
        logging.error(f"Error analyzing text with Gemini: {str(e)}")
        return None

def get_place_reviews(place_id):
    """
    Get reviews for a specific place
    """
    try:
        place_details = gmaps.place(
            place_id=place_id,
            language='vi',
            fields=['name', 'review', 'formatted_address', 'geometry', 'rating', 'type']
        )
        
        return place_details.get('result', {}).get('reviews', [])
    except Exception as e:
        logging.error(f"Error getting reviews for place {place_id}: {str(e)}")
        return []

def is_elderly_friendly(place_id, place_types):
    """
    Determine if a place is elderly-friendly based on reviews and metadata
    """
    reviews = get_place_reviews(place_id)
    print(reviews)
    if not reviews:
        return {'is_friendly': False, 'confidence': 0, 'reasons': ["No reviews available"]}
    
    elderly_friendly_score = 0
    reasons = []
    
    # Check place types for relevant facilities
    elderly_friendly_types = ['hospital', 'doctor', 'pharmacy', 'physiotherapist', 'health', 'elevator']
    for place_type in place_types:
        if place_type in elderly_friendly_types:
            elderly_friendly_score += 1
            reasons.append(f"Place type is {place_type}")
    
    # Analyze reviews
    analyzed_reviews = []
    for review in reviews:
        review_text = review.get('text', '')
        if not review_text:
            continue
            
        analysis = analyze_review_text(review_text)
        if not analysis:
            continue
            
        # Score based on keywords in reviews
        if analysis['elderly_keywords']:
            keywords_found = ", ".join(analysis['elderly_keywords'])
            elderly_friendly_score += 2
            reasons.append(f"Review mentions: {keywords_found}")
            
        # Score based on sentiment of reviews with elderly keywords
        if analysis['elderly_keywords'] and analysis['sentiment_score'] > 0:
            elderly_friendly_score += 1
            reasons.append(f"Positive sentiment with elderly keywords")
            
        analyzed_reviews.append({
            'review_text': review_text[:100] + '...' if len(review_text) > 100 else review_text,
            'analysis': analysis
        })
    
    # Calculate confidence score (0-100%)
    confidence = min(100, (elderly_friendly_score / (len(reviews) + 2)) * 100)
    
    return {
        'is_friendly': elderly_friendly_score > 0,
        'confidence': confidence,
        'reasons': reasons,
        'analyzed_reviews': analyzed_reviews[:3]  # Only include first 3 analyzed reviews
    }

def search_elderly_friendly_places(location, types, radius=5000, min_confidence=30):
    """
    Search for elderly-friendly places in the given location
    """
    results = []
    max_places = 3  # Limit to 3 places for testing
    
    try:
        # Search for places
        places_result = gmaps.places_nearby(
            location=location,
            radius=radius,
            type=types
        )
        
        if not places_result.get('results'):
            logging.warning(f"No places found for type {types} in {location}")
            return results
            
        for place in places_result.get('results', [])[:max_places]:  # Only process first 3 places
            place_id = place.get('place_id')
            place_name = place.get('name')
            place_types = place.get('types', [])
            
            logging.info(f"Analyzing place: {place_name}")
            
            # Determine if place is elderly-friendly
            elderly_analysis = is_elderly_friendly(place_id, place_types)
            
            if elderly_analysis['is_friendly'] and elderly_analysis['confidence'] >= min_confidence:
                place_details = {
                    'place_id': place_id,
                    'name': place_name,
                    'address': place.get('vicinity', ''),
                    'location': place.get('geometry', {}).get('location', {}),
                    'types': place_types,
                    'rating': place.get('rating'),
                    'user_ratings_total': place.get('user_ratings_total'),
                    'elderly_friendly': elderly_analysis
                }
                results.append(place_details)
                logging.info(f"Found elderly-friendly place: {place_name} (confidence: {elderly_analysis['confidence']:.1f}%)")
    
    except Exception as e:
        logging.error(f"Error searching for places: {str(e)}")
    
    return results

def save_to_file(places, filename='elderly_friendly_places'):
    """
    Save results to a JSON file
    """
    if not places:
        logging.warning("No places to save")
        return
        
    output_dir = os.path.join('output', 'elderly_friendly')
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    full_filename = f"{filename}_{timestamp}.json"
    
    with open(os.path.join(output_dir, full_filename), 'w', encoding='utf-8') as f:
        json.dump(places, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Saved {len(places)} elderly-friendly places to {os.path.join(output_dir, full_filename)}")

def main():
    # Hanoi coordinates
    hanoi_location = (21.0278, 105.8342)  # Latitude, Longitude for Hanoi
    
    # Place types to search for
    place_types = [
        'lodging',        # Hotels and accommodations
        'restaurant',     # Restaurants
        'tourist_attraction',  # Tourist attractions
        'museum',         # Museums
        'shopping_mall',  # Shopping malls
        'hospital',       # Hospitals
        'pharmacy',       # Pharmacies
        'cafe'            # Cafes
    ]
    
    all_elderly_friendly_places = []
    
    for place_type in place_types:
        logging.info(f"Searching for elderly-friendly {place_type} in Hanoi")
        places = search_elderly_friendly_places(
            location=hanoi_location,
            types=place_type,
            radius=10000,  # 10km radius
            min_confidence=1  # At least 30% confidence
        )
        
        if places:
            all_elderly_friendly_places.extend(places)
            save_to_file(places, f"elderly_friendly_{place_type}")
    
    # Save all places in one file
    save_to_file(all_elderly_friendly_places, "all_elderly_friendly_places")
    
    logging.info(f"Found a total of {len(all_elderly_friendly_places)} elderly-friendly places in Hanoi")

if __name__ == "__main__":
    main() 