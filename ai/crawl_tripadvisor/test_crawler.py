#!/usr/bin/env python3
# Test script for TripAdvisor crawler
import unittest
import os
import sys
import csv
from tripadvisor_crawler import TripAdvisorCrawler

class TestTripAdvisorCrawler(unittest.TestCase):
    def setUp(self):
        # Create a crawler with a longer delay to avoid rate limiting during tests
        self.crawler = TripAdvisorCrawler(delay=5)
        
        # Create a data directory for test outputs
        os.makedirs('test_data', exist_ok=True)
    
    def test_attraction_details(self):
        """Test the extraction of attraction details"""
        # Test on a well-known attraction
        attraction_url = "https://www.tripadvisor.com/Attraction_Review-g293924-d317503-Reviews-Old_Quarter-Hanoi.html"
        details = self.crawler.get_attraction_details(attraction_url)
        
        # Check that we got the basic fields
        self.assertIn('name', details)
        self.assertIn('url', details)
        
        # Print all extracted fields for manual verification
        print("\n--- Attraction Details ---")
        for key, value in details.items():
            print(f"{key}: {value}")
        
        # Verify some specific fields
        self.assertEqual(details['url'], attraction_url)
        self.assertIn('Old Quarter', details['name'])
        
        # Check that the category is correctly identified
        self.assertIn('category', details)
        
    def test_hotel_details(self):
        """Test the extraction of hotel details"""
        # Test on a well-known hotel
        hotel_url = "https://www.tripadvisor.com/Hotel_Review-g293924-d301984-Reviews-Sofitel_Legend_Metropole_Hanoi-Hanoi.html"
        details = self.crawler.get_attraction_details(hotel_url)
        
        # Print all extracted fields for manual verification
        print("\n--- Hotel Details ---")
        for key, value in details.items():
            print(f"{key}: {value}")
        
        # Verify some specific fields
        self.assertEqual(details['url'], hotel_url)
        self.assertIn('Sofitel', details['name'])
        
        # Hotels should have price_level and rating
        self.assertIn('rating', details)
        
    def test_restaurant_details(self):
        """Test the extraction of restaurant details"""
        # Test on a well-known restaurant
        restaurant_url = "https://www.tripadvisor.com/Restaurant_Review-g293924-d8288571-Reviews-Bun_Cha_Huong_Lien-Hanoi.html"
        details = self.crawler.get_attraction_details(restaurant_url)
        
        # Print all extracted fields for manual verification
        print("\n--- Restaurant Details ---")
        for key, value in details.items():
            print(f"{key}: {value}")
        
        # Verify some specific fields
        self.assertEqual(details['url'], restaurant_url)
        self.assertIn('Bun Cha', details['name'])
        
        # Restaurants should have price_level
        self.assertIn('price_level', details)
    
    def test_get_attractions(self):
        """Test getting a list of attractions"""
        attractions_url = "https://www.tripadvisor.com/Attractions-g293924-Activities-Hanoi.html"
        attractions = self.crawler.get_attractions(attractions_url)
        
        # Check that we got some attractions
        self.assertTrue(len(attractions) > 0)
        print(f"\nFound {len(attractions)} attractions")
        
        # Check first 3 attractions
        for i, attraction in enumerate(attractions[:3]):
            print(f"{i+1}. {attraction['name']} - {attraction['url']}")
            
        # Validate structure
        self.assertIn('name', attractions[0])
        self.assertIn('url', attractions[0])
    
    def test_full_scrape(self):
        """Test a complete scrape operation with output"""
        output_file = "test_data/hanoi_test.csv"
        attractions_url = "https://www.tripadvisor.com/Attractions-g293924-Activities-Hanoi.html"
        
        # Scrape just 2 attractions to keep the test short
        self.crawler.scrape_location(
            location_url=attractions_url,
            max_attractions=2,
            output_file=output_file
        )
        
        # Verify the output file exists
        self.assertTrue(os.path.exists(output_file))
        
        # Check the contents
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Should have 2 rows
            self.assertEqual(len(rows), 2)
            
            # Print field names
            print("\n--- CSV Fields ---")
            print(reader.fieldnames)
            
            # Check for key required fields
            self.assertIn('name', reader.fieldnames)
            self.assertIn('url', reader.fieldnames)
            self.assertIn('rating', reader.fieldnames)
            
            # Print first row for verification
            print("\n--- First Row Data ---")
            for key, value in rows[0].items():
                print(f"{key}: {value}")

if __name__ == "__main__":
    unittest.main() 