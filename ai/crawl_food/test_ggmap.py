import requests
import json

API_KEY = 'AIzaSyD8vcgWfKnRu0gF8IE1XcUxqypSZCgrxc8'  # Sử dụng API key của bạn
PLACE_ID = 'ChIJ8T5rQm0rNTERKQeD0lD2nU8'  # Place ID của một nhà hàng cụ thể

def test_place_details():
    # URL cho Place Details API với tất cả các field có thể có
    fields = [
        'name', 'rating', 'formatted_address', 'geometry', 'reviews',
        'user_ratings_total', 'photos', 'opening_hours', 'website',
        'formatted_phone_number', 'price_level', 'types', 'vicinity',
        'url', 'utc_offset', 'address_components', 'adr_address',
        'business_status', 'icon', 'icon_background_color', 'icon_mask_base_uri',
        'international_phone_number', 'permanently_closed', 'place_id',
        'plus_code', 'scope', 'reference'
    ]
    
    fields_str = ','.join(fields)
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={PLACE_ID}&fields={fields_str}&key={API_KEY}"
    
    try:
        response = requests.get(details_url)
        data = response.json()
        
        if data.get('status') == 'OK':
            result = data.get('result', {})
            
            # In ra tất cả các field có giá trị
            print("\n=== Các field có giá trị ===")
            for field, value in result.items():
                if value:  # Chỉ in các field có giá trị
                    print(f"\n{field}:")
                    print(json.dumps(value, indent=2, ensure_ascii=False))
            
            # In ra các field không có giá trị
            print("\n=== Các field không có giá trị ===")
            for field in fields:
                if field not in result or not result[field]:
                    print(f"- {field}")
        
        else:
            print(f"Lỗi: {data.get('status')}")
            print(f"Thông báo: {data.get('error_message', 'Không có thông báo lỗi')}")
            
    except Exception as e:
        print(f"Lỗi khi gọi API: {str(e)}")

if __name__ == "__main__":
    test_place_details() 