import pandas as pd
import os
import json
from datetime import datetime
import re
from urllib.parse import urljoin
import numpy as np
from pathlib import Path
import csv

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

def extract_location(text):
    """Extract location (province) from text"""
    if not text or pd.isna(text):
        return None
    
    # Danh sách các tỉnh/thành phố ở Việt Nam
    provinces = [
        "Hà Nội", "TP.HCM", "Hồ Chí Minh", "Sài Gòn", "Đà Nẵng", "Hải Phòng", "Cần Thơ",
        "An Giang", "Bà Rịa - Vũng Tàu", "Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu",
        "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau",
        "Cao Bằng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai",
        "Hà Giang", "Hà Nam", "Hà Tĩnh", "Hải Dương", "Hậu Giang", "Hòa Bình", "Hưng Yên",
        "Khánh Hòa", "Nha Trang", "Kiên Giang", "Phú Quốc", "Kon Tum", "Lai Châu", "Lâm Đồng", 
        "Đà Lạt", "Lạng Sơn", "Lào Cai", "Sapa", "Long An", "Nam Định", "Nghệ An", "Ninh Bình",
        "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình", "Quảng Nam", "Hội An", "Quảng Ngãi",
        "Quảng Ninh", "Hạ Long", "Quảng Trị", "Sóc Trăng", "Sơn La", "Mộc Châu", "Tây Ninh", "Thái Bình",
        "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Huế", "Tiền Giang", "Trà Vinh", "Tuyên Quang",
        "Vĩnh Long", "Vĩnh Phúc", "Yên Bái", "Côn Đảo", "Phú Quý", "Lý Sơn"
    ]
    
    text = text.lower()
    results = []
    
    for province in provinces:
        if province.lower() in text:
            results.append(province)
    
    # Trường hợp đặc biệt
    if "miền bắc" in text:
        results.append("Miền Bắc")
    if "miền trung" in text:
        results.append("Miền Trung")
    if "miền nam" in text:
        results.append("Miền Nam")
    if "miền tây" in text:
        results.append("Miền Tây")
    if "tây bắc" in text:
        results.append("Tây Bắc")
    if "đông bắc" in text:
        results.append("Đông Bắc")
    if "tây nguyên" in text:
        results.append("Tây Nguyên")
    
    return ", ".join(results) if results else "Không xác định"

def process_csv():
    # Define file paths
    csv_file = os.path.join('data', 'dulichviet.csv')
    output_file = os.path.join('data', 'processed_tours.json')
    output_csv = os.path.join('data', 'processed_tours.csv')
    
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
            # Extract location information
            all_text = f"{row.get('mda-box-name', '')} {row.get('mda-box-des 2', '')} {row.get('des', '')}"
            location = extract_location(all_text)
            
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
                "location": location,
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
                tour["days"] = duration["days"]
                tour["nights"] = duration["nights"]
            
            # Extract departure dates
            departure_dates = extract_departure_dates(row["mda-lb"])
            if departure_dates:
                tour["extracted_dates"] = departure_dates
                tour["departure_dates_count"] = len(departure_dates)
            
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
    
    # Save processed data as JSON
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        print(f"\nSuccessfully processed and saved {len(processed_data)} tours to {output_file}")
    except Exception as e:
        print(f"Error saving processed data to JSON: {e}")
    
    # Save processed data as CSV
    try:
        # Extract keys from all tours to ensure we have all fields
        all_keys = set()
        for tour in processed_data:
            all_keys.update(tour.keys())
        
        # Remove complex fields that can't be easily represented in CSV
        keys_to_remove = ["duration", "extracted_dates"]
        csv_keys = [k for k in all_keys if k not in keys_to_remove]
        
        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_keys)
            writer.writeheader()
            
            for tour in processed_data:
                # Create a new dict with only the keys for CSV
                row = {k: tour.get(k, '') for k in csv_keys}
                writer.writerow(row)
                
        print(f"Successfully saved {len(processed_data)} tours to CSV: {output_csv}")
    except Exception as e:
        print(f"Error saving processed data to CSV: {e}")
    
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
    
    # Save each category to a separate file (JSON)
    for category, tours in categories.items():
        filename = category.lower().replace(" ", "_") + ".json"
        output_file = os.path.join(output_dir, filename)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tours, f, ensure_ascii=False, indent=2)
            print(f"Exported {len(tours)} tours to {output_file}")
            
            # Also save as CSV
            csv_file = os.path.join(output_dir, category.lower().replace(" ", "_") + ".csv")
            
            # Extract keys from all tours in this category
            all_keys = set()
            for tour in tours:
                all_keys.update(tour.keys())
            
            # Remove complex fields that can't be easily represented in CSV
            keys_to_remove = ["duration", "extracted_dates"]
            csv_keys = [k for k in all_keys if k not in keys_to_remove]
            
            with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=csv_keys)
                writer.writeheader()
                
                for tour in tours:
                    # Create a new dict with only the keys for CSV
                    row = {k: tour.get(k, '') for k in csv_keys}
                    writer.writerow(row)
                    
            print(f"Exported {len(tours)} tours to CSV: {csv_file}")
            
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
    
    # Location statistics
    locations = [tour.get("location") for tour in data if tour.get("location")]
    if locations:
        location_counts = {}
        for location in locations:
            if "," in location:
                # Split multiple locations and count each
                for loc in location.split(", "):
                    location_counts[loc] = location_counts.get(loc, 0) + 1
            else:
                location_counts[location] = location_counts.get(location, 0) + 1
        
        print(f"Top locations:")
        for location, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {location}: {count} tours")

def main():
    print("Starting CSV processing...")
    process_csv()
    print("Done!")

if __name__ == "__main__":
    main()