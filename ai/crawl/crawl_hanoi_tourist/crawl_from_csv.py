import pandas as pd
import os
import json
from datetime import datetime
import re
from urllib.parse import urljoin
import numpy as np
from pathlib import Path

def clean_text(text):
    """Clean text by removing extra whitespaces and special characters"""
    if not text or pd.isna(text):
        return ""
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_price(text):
    """Extract price from text"""
    if not text or pd.isna(text):
        return None
    
    # Look for price patterns like "9,299,000 đ" or "9.299.000 VND"
    price_match = re.search(r'([\d,.]+)(\s*đ|\s*₫|VND|Đ)', str(text))
    if price_match:
        price_str = price_match.group(1).replace('.', '').replace(',', '')
        try:
            return int(price_str)
        except ValueError:
            return None
    return None

def extract_duration(text):
    """Extract duration from text"""
    if not text or pd.isna(text):
        return None
    
    duration_match = re.search(r'(\d+)\s*ngày\s*(\d*)\s*đêm', str(text))
    if duration_match:
        days = int(duration_match.group(1))
        nights = int(duration_match.group(2)) if duration_match.group(2) else days - 1
        return {"days": days, "nights": nights}
    return None

def extract_departure_dates(text):
    """Extract departure dates from text"""
    if not text or pd.isna(text):
        return []
    
    # Look for date patterns like "01/02/2025" or "01,02/05/2025"
    dates = []
    date_pattern = r'(\d{1,2})[/,-](\d{1,2})[/,-](\d{4})'
    matches = re.finditer(date_pattern, str(text))
    
    for match in matches:
        day, month, year = match.groups()
        dates.append(f"{day.zfill(2)}/{month.zfill(2)}/{year}")
    
    return dates

def process_csv():
    # Define file paths
    csv_file = os.path.join('data', 'dulichviet.csv')
    output_file = os.path.join('data', 'processed_tours.json')
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File {csv_file} not found!")
        return
    
    # Read CSV file
    print(f"Reading CSV file: {csv_file}")
    try:
        df = pd.read_csv(csv_file)
        print(f"Successfully read CSV with {len(df)} rows and {len(df.columns)} columns")
        print("Columns:", df.columns.tolist())
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Initial data exploration
    print("\nData Sample:")
    print(df.head(2))
    
    print("\nMissing values per column:")
    print(df.isna().sum())
    
    # Process the data
    print("\nProcessing data...")
    processed_data = []
    
    base_url = "https://dulichviet.com.vn"
    
    for _, row in df.iterrows():
        try:
            tour = {
                "source_url": urljoin(base_url, row["mda-box-img href"]) if not pd.isna(row["mda-box-img href"]) else "",
                "image_url": clean_text(row["lazy src"]),
                "origin": clean_text(row["mda-box-lb"]),
                "description": clean_text(row["des"]),
                "name": clean_text(row["mda-box-name"]),
                "short_description": clean_text(row["mda-box-des 2"]),
                "duration_text": clean_text(row["mda-time 2"]),
                "schedule": clean_text(row["mda-day"]),
                "departure_dates": clean_text(row["mda-lb"]),
                "processed_at": datetime.now().isoformat(),
            }
            
            # Try to extract price from multiple columns
            price = None
            for col in ["mda-day", "des", "mda-box-des 2"]:
                if col in row and not pd.isna(row[col]):
                    price = extract_price(row[col])
                    if price:
                        break
            
            if price:
                tour["price"] = price
            
            # Extract duration
            duration = extract_duration(row["mda-time 2"])
            if duration:
                tour["duration"] = duration
            
            # Extract departure dates
            departure_dates = extract_departure_dates(row["mda-lb"])
            if departure_dates:
                tour["extracted_dates"] = departure_dates
            
            # Add category based on the name or description
            if any(word in tour["name"].lower() for word in ["hà nội", "hanoi"]):
                tour["category"] = "Hanoi Tours"
            elif "hạ long" in tour["name"].lower() or "halong" in tour["name"].lower():
                tour["category"] = "Halong Bay Tours"
            elif "sapa" in tour["name"].lower():
                tour["category"] = "Sapa Tours"
            elif "miền bắc" in tour["name"].lower() or "mien bac" in tour["name"].lower():
                tour["category"] = "Northern Vietnam Tours"
            elif "miền trung" in tour["name"].lower() or "mien trung" in tour["name"].lower():
                tour["category"] = "Central Vietnam Tours"
            elif "miền nam" in tour["name"].lower() or "mien nam" in tour["name"].lower():
                tour["category"] = "Southern Vietnam Tours"
            elif "miền tây" in tour["name"].lower() or "mien tay" in tour["name"].lower():
                tour["category"] = "Mekong Delta Tours"
            else:
                tour["category"] = "Other Tours"
            
            processed_data.append(tour)
        except Exception as e:
            print(f"Error processing row: {e}")
            continue
    
    # Save processed data
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        print(f"\nSuccessfully processed and saved {len(processed_data)} tours to {output_file}")
    except Exception as e:
        print(f"Error saving processed data: {e}")
    
    # Generate stats about the data
    generate_stats(processed_data)
    
    # Export categorized data
    export_categorized_data(processed_data)

def export_categorized_data(data):
    """Export data by categories"""
    categories = {}
    
    # Group tours by category
    for tour in data:
        category = tour.get("category", "Other Tours")
        if category not in categories:
            categories[category] = []
        categories[category].append(tour)
    
    # Create a directory for categories
    output_dir = os.path.join('data', 'categories')
    os.makedirs(output_dir, exist_ok=True)
    
    # Save each category to a separate file
    for category, tours in categories.items():
        filename = category.lower().replace(" ", "_") + ".json"
        output_file = os.path.join(output_dir, filename)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tours, f, ensure_ascii=False, indent=2)
            print(f"Exported {len(tours)} tours to {output_file}")
        except Exception as e:
            print(f"Error exporting {category}: {e}")

def generate_stats(data):
    """Generate and print statistics about the processed data"""
    print("\n=== Dataset Statistics ===")
    
    # Count total tours
    print(f"Total tours: {len(data)}")
    
    # Count tours with images
    has_image = sum(1 for tour in data if tour.get("image_url"))
    print(f"Tours with images: {has_image} ({has_image/len(data)*100:.2f}%)")
    
    # Price statistics
    prices = [tour.get("price") for tour in data if tour.get("price")]
    if prices:
        print(f"Price statistics:")
        print(f"  - Min price: {min(prices):,} VND")
        print(f"  - Max price: {max(prices):,} VND")
        print(f"  - Average price: {sum(prices)/len(prices):,.2f} VND")
    
    # Duration statistics
    durations = [tour.get("duration", {}).get("days") for tour in data if tour.get("duration")]
    if durations:
        print(f"Duration statistics:")
        print(f"  - Min duration: {min(durations)} days")
        print(f"  - Max duration: {max(durations)} days")
        print(f"  - Most common duration: {max(set(durations), key=durations.count)} days")
    
    # Origin statistics
    origins = [tour.get("origin") for tour in data if tour.get("origin")]
    if origins:
        origin_counts = {}
        for origin in origins:
            origin_counts[origin] = origin_counts.get(origin, 0) + 1
        
        print(f"Top origins:")
        for origin, count in sorted(origin_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {origin}: {count} tours")
    
    # Category statistics
    categories = [tour.get("category") for tour in data if tour.get("category")]
    if categories:
        category_counts = {}
        for category in categories:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print(f"Category distribution:")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {category}: {count} tours ({count/len(data)*100:.2f}%)")

def main():
    print("Starting CSV processing...")
    process_csv()
    print("Done!")

if __name__ == "__main__":
    main()