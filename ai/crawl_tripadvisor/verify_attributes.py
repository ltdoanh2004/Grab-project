#!/usr/bin/env python3
from tripadvisor_crawler import TripAdvisorCrawler
import json
import sys
import time

def main():
    # Define sample URLs for each entity type
    urls = {
        "attraction": "https://www.tripadvisor.com/Attraction_Review-g293924-d317503-Reviews-Old_Quarter-Hanoi.html",
        "hotel": "https://www.tripadvisor.com/Hotel_Review-g293924-d301984-Reviews-Sofitel_Legend_Metropole_Hanoi-Hanoi.html",
        "restaurant": "https://www.tripadvisor.com/Restaurant_Review-g293925-d7153258-Reviews-Hum_Vegetarian_Lounge_Restaurant-Ho_Chi_Minh_City.html"
    }
    
    # Required attributes to check for
    required_attributes = [
        "name", "category", "location", "latitude", "longitude", "rating", 
        "number_of_reviews", "review_summary", "price_level", "recommended_duration", 
        "tags", "suitable_for", "opening_hours", "image_url", "activities", 
        "website", "contact_info", "popular_times", "nearby_places", 
        "review_date", "reviewer_origin", "rank_in_city"
    ]
    
    # Create crawler with short delay for testing
    crawler = TripAdvisorCrawler(delay=1)
    
    # Check each entity type
    for entity_type, url in urls.items():
        print(f"\n===== Testing {entity_type.upper()} =====")
        print(f"URL: {url}")
        
        # Get details
        start_time = time.time()
        details = crawler.get_attraction_details(url)
        end_time = time.time()
        
        # Print all extracted fields
        print(f"\nExtracted {len(details)} attributes in {end_time - start_time:.2f} seconds:")
        for key, value in details.items():
            # Format the output for better readability
            if isinstance(value, list) and len(value) > 3:
                value = f"{value[:3]} + {len(value) - 3} more"
            elif isinstance(value, str) and len(value) > 100:
                value = value[:97] + "..."
                
            print(f"  - {key}: {value}")
        
        # Check for missing required attributes
        missing = [attr for attr in required_attributes if attr not in details]
        if missing:
            print(f"\nMissing {len(missing)}/{len(required_attributes)} required attributes:")
            for attr in missing:
                print(f"  - {attr}")
        else:
            print(f"\nAll {len(required_attributes)} required attributes were extracted!")
    
    print("\nVerification complete!")

if __name__ == "__main__":
    main() 