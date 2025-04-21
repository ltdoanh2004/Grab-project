import requests
import json
import time

API_KEY = 'AIzaSyCUDjLLa0_XID0OZvB9X2Io_CDIPTCgc1Q'  # ⚠️ Thay bằng API key của bạn
location = '21.0285,105.8542'  # Ví dụ: Hà Nội
radius = 1500  # mét
type_place = 'restaurant'

# Lưu kết quả
results = []

# Step 1: Nearby Search API
nearby_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&type={type_place}&key={API_KEY}"
response = requests.get(nearby_url)
data = response.json()

for place in data.get("results", []):
    place_id = place["place_id"]
    
    # Step 2: Place Details API
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,rating,formatted_address,geometry,reviews,user_ratings_total,photos&key={API_KEY}"
    details = requests.get(details_url).json().get("result", {})

    # Step 3: Lấy ảnh (nếu có)
    photo_url = ""
    if "photos" in details:
        photo_ref = details["photos"][0]["photo_reference"]
        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={API_KEY}"

    # Step 4: Review (lấy tối đa 3)
    reviews = []
    for r in details.get("reviews", [])[:3]:
        reviews.append({
            "author": r.get("author_name"),
            "rating": r.get("rating"),
            "text": r.get("text")
        })

    # Step 5: Gộp lại
    results.append({
        "name": details.get("name"),
        "address": details.get("formatted_address"),
        "rating": details.get("rating"),
        "total_ratings": details.get("user_ratings_total"),
        "location": details.get("geometry", {}).get("location"),
        "photo_url": photo_url,
        "reviews": reviews
    })

    time.sleep(1)  # Giới hạn tốc độ tránh bị block

# Save to JSON
with open("restaurants_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("✅ Done. Dữ liệu đã được lưu vào restaurants_data.json")
