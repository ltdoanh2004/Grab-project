import googlemaps
import json
import time
from datetime import datetime
import pandas as pd
import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import requests
from urllib.parse import urlencode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawl.log'),
        logging.StreamHandler()
    ]
)

# Khởi tạo client Google Maps với API key
API_KEY = 'AIzaSyBPRDc8Sp3M_tlv0VYZOW2WIA6SCbBHYWM'  # Thay thế bằng API key của bạn
gmaps = googlemaps.Client(key=API_KEY)

# Counter for tracking API quota
api_quota_counter = 0
MAX_DAILY_QUOTA = 1000  # Adjust based on your plan

def increment_api_counter():
    """Increment API counter and log current usage"""
    global api_quota_counter
    api_quota_counter += 1
    if api_quota_counter % 10 == 0:
        logging.info(f"API queries_quota: {api_quota_counter}")

def get_city_centers(location):
    """
    Lấy danh sách các trung tâm tìm kiếm trong thành phố
    """
    try:
        # Lấy tọa độ trung tâm thành phố
        geocode_result = gmaps.geocode(location)
        increment_api_counter()
        if not geocode_result:
            logging.error(f"Không tìm thấy vị trí: {location}")
            return []
            
        center = geocode_result[0]['geometry']['location']
        
        # Tạo các điểm tìm kiếm xung quanh trung tâm
        # Mỗi điểm cách nhau khoảng 7.5km (giảm từ 15km)
        centers = []
        radius_km = 7.5
        for lat_offset in [-2, -1, 0, 1, 2]:
            for lng_offset in [-2, -1, 0, 1, 2]:
                new_lat = center['lat'] + (lat_offset * radius_km / 111)  # 1 độ ~ 111km
                new_lng = center['lng'] + (lng_offset * radius_km / 111)
                centers.append({'lat': new_lat, 'lng': new_lng})
        
        # Thêm các quận/huyện chính của Hà Nội
        districts = [
            "Hoàn Kiếm, Hà Nội",
            "Ba Đình, Hà Nội",
            "Đống Đa, Hà Nội",
            "Hai Bà Trưng, Hà Nội",
            "Cầu Giấy, Hà Nội",
            "Thanh Xuân, Hà Nội",
            "Hoàng Mai, Hà Nội",
            "Long Biên, Hà Nội",
            "Tây Hồ, Hà Nội",
            "Nam Từ Liêm, Hà Nội",
            "Bắc Từ Liêm, Hà Nội",
            "Hà Đông, Hà Nội"
        ]
        
        for district in districts:
            try:
                district_result = gmaps.geocode(district)
                increment_api_counter()
                if district_result:
                    district_center = district_result[0]['geometry']['location']
                    centers.append({
                        'lat': district_center['lat'],
                        'lng': district_center['lng']
                    })
            except Exception as e:
                logging.warning(f"Không thể lấy tọa độ của {district}: {str(e)}")
                continue
        
        logging.info(f"Đã tạo {len(centers)} điểm tìm kiếm cho {location}")
        return centers
    except Exception as e:
        logging.error(f"Lỗi khi lấy trung tâm thành phố: {str(e)}")
        return []

def get_place_photos(place_id, max_photos=10):
    """
    Lấy danh sách hình ảnh của địa điểm
    """
    try:
        # Lấy thông tin chi tiết của địa điểm bao gồm photos
        place_details = gmaps.place(
            place_id,
            language='vi',
            fields=['photo']
        )
        increment_api_counter()
        
        photo_references = []
        photos = place_details.get('result', {}).get('photos', [])
        
        # Giới hạn số lượng ảnh
        for photo in photos[:max_photos]:
            if 'photo_reference' in photo:
                # Tạo URL để tải ảnh
                photo_url = "https://maps.googleapis.com/maps/api/place/photo"
                params = {
                    'maxwidth': 800,  # Kích thước ảnh
                    'photoreference': photo['photo_reference'],
                    'key': API_KEY
                }
                photo_references.append({
                    'url': f"{photo_url}?{urlencode(params)}",
                    'width': photo.get('width'),
                    'height': photo.get('height'),
                    'html_attributions': photo.get('html_attributions', [])
                })
                
        return photo_references
        
    except Exception as e:
        logging.error(f"Lỗi khi lấy hình ảnh địa điểm: {str(e)}")
        return []

def get_price_range_text(price_level):
    """
    Chuyển đổi giá trị price_level thành mô tả giá
    """
    if price_level == 0:
        return "Miễn phí"
    elif price_level == 1:
        return "Rẻ"
    elif price_level == 2:
        return "Trung bình"
    elif price_level == 3:
        return "Đắt"
    elif price_level == 4:
        return "Rất đắt"
    else:
        return "N/A"

def search_places(query, location="Hà Nội, Việt Nam", radius=15000, max_results_per_type=1500):
    """
    Tìm kiếm địa điểm dựa trên từ khóa và vị trí
    """
    try:
        # Lấy danh sách các trung tâm tìm kiếm
        centers = get_city_centers(location)
        if not centers:
            return []
            
        places = []
        total_results = 0
        max_retries = 3
        retry_delay = 5  # seconds
        place_details_delay = 2  # seconds between place details requests (reduced to optimize)
        last_place_details_time = 0
        
        # Tìm kiếm từ mỗi trung tâm
        for center in centers:
            if total_results >= max_results_per_type:
                break
                
            next_page_token = None
            retry_count = 0
            
            while True:
                # Kiểm tra nếu đã đạt giới hạn
                if total_results >= max_results_per_type:
                    logging.info(f"Đã đạt giới hạn {max_results_per_type} địa điểm cho loại {query}")
                    break
                    
                # Check API quota
                if api_quota_counter >= MAX_DAILY_QUOTA:
                    logging.warning(f"Đã đạt giới hạn API hàng ngày ({MAX_DAILY_QUOTA}). Dừng crawl.")
                    return places
                
                try:
                    # Tìm kiếm địa điểm
                    places_result = gmaps.places(
                        query,
                        location=(center['lat'], center['lng']),
                        language='vi',
                        region='VN',
                        radius=radius,
                        page_token=next_page_token if next_page_token else None
                    )
                    increment_api_counter()
                    
                    if not places_result.get('results'):
                        break
                        
                    for place in places_result.get('results', []):
                        # Kiểm tra nếu đã đạt giới hạn
                        if total_results >= max_results_per_type:
                            break
                            
                        # Kiểm tra trùng lặp
                        if any(p['place_id'] == place['place_id'] for p in places):
                            continue
                            
                        try:
                            # Rate limiting cho place details
                            current_time = time.time()
                            time_since_last_request = current_time - last_place_details_time
                            if time_since_last_request < place_details_delay:
                                sleep_time = place_details_delay - time_since_last_request
                                logging.info(f"Đợi {sleep_time:.1f} giây trước khi lấy thông tin chi tiết...")
                                time.sleep(sleep_time)
                            
                            # Lấy thông tin chi tiết của địa điểm với nhiều trường hơn
                            place_details = gmaps.place(
                                place['place_id'],
                                language='vi',
                                fields=[
                                    'name', 'formatted_address', 'formatted_phone_number', 
                                    'rating', 'user_ratings_total', 'opening_hours', 
                                    'price_level', 'website', 'url', 'review',
                                    'business_status', 'geometry', 'editorial_summary',
                                    'current_opening_hours', 'delivery', 'dine_in', 
                                    'reservable', 'serves_breakfast', 'serves_lunch', 
                                    'serves_dinner', 'takeout', 'wheelchair_accessible_entrance',
                                    'plus_code', 'international_phone_number', 'adr_address',
                                    'utc_offset', 'vicinity', 'permanently_closed',
                                    'serves_beer', 'serves_wine', 'serves_vegetarian_food',
                                    'curbside_pickup'
                                ]
                            )['result']
                            increment_api_counter()
                            
                            last_place_details_time = time.time()
                            
                            # Lấy hình ảnh của địa điểm
                            photos = get_place_photos(place['place_id'], max_photos=5)
                            
                            # Xác định type dựa trên query
                            place_type = query.lower()
                            
                            # Chuyển đổi giá trị price_level thành mô tả
                            price_level = place_details.get('price_level', None)
                            price_description = get_price_range_text(price_level)
                            
                            # Tạo dictionary chứa thông tin địa điểm
                            place_info = {
                                'name': place_details.get('name', 'N/A'),
                                'address': place_details.get('formatted_address', 'N/A'),
                                'vicinity': place_details.get('vicinity', 'N/A'),
                                'phone': place_details.get('formatted_phone_number', 'N/A'),
                                'international_phone': place_details.get('international_phone_number', 'N/A'),
                                'rating': place_details.get('rating', 'N/A'),
                                'total_ratings': place_details.get('user_ratings_total', 'N/A'),
                                'price_level': price_level,
                                'price_description': price_description,
                                'website': place_details.get('website', 'N/A'),
                                'google_maps_url': place_details.get('url', 'N/A'),
                                'business_status': place_details.get('business_status', 'N/A'),
                                'permanently_closed': place_details.get('permanently_closed', False),
                                'type': place_type,
                                'place_id': place['place_id'],
                                'location': place_details.get('geometry', {}).get('location', {}),
                                'photos': photos,
                                'editorial_summary': place_details.get('editorial_summary', {}).get('overview', 'N/A'),
                                'plus_code': place_details.get('plus_code', 'N/A'),
                                'utc_offset': place_details.get('utc_offset', 'N/A')
                            }
                            
                            # Thêm giờ mở cửa nếu có
                            if 'opening_hours' in place_details:
                                place_info['opening_hours'] = place_details['opening_hours'].get('weekday_text', [])
                                place_info['open_now'] = place_details['opening_hours'].get('open_now', False)
                            else:
                                place_info['opening_hours'] = []
                                place_info['open_now'] = False

                            # Thêm giờ mở cửa hiện tại nếu có
                            if 'current_opening_hours' in place_details:
                                place_info['current_opening_hours'] = place_details['current_opening_hours'].get('weekday_text', [])
                                place_info['current_open_now'] = place_details['current_opening_hours'].get('open_now', False)
                            
                            # Thêm các thông tin về dịch vụ
                            place_info['features'] = {
                                'delivery': place_details.get('delivery', False),
                                'dine_in': place_details.get('dine_in', False),
                                'takeout': place_details.get('takeout', False),
                                'reservable': place_details.get('reservable', False),
                                'serves_breakfast': place_details.get('serves_breakfast', False),
                                'serves_lunch': place_details.get('serves_lunch', False),
                                'serves_dinner': place_details.get('serves_dinner', False),
                                'wheelchair_accessible': place_details.get('wheelchair_accessible_entrance', False),
                                'serves_beer': place_details.get('serves_beer', False),
                                'serves_wine': place_details.get('serves_wine', False),
                                'serves_vegetarian_food': place_details.get('serves_vegetarian_food', False),
                                'curbside_pickup': place_details.get('curbside_pickup', False)
                            }
                            
                            # Thêm đánh giá nếu có
                            if 'review' in place_details:
                                reviews = place_details['review']
                                place_info['reviews'] = [{
                                    'author_name': review.get('author_name', 'N/A'),
                                    'rating': review.get('rating', 'N/A'),
                                    'time': review.get('time', 'N/A'),
                                    'text': review.get('text', 'N/A'),
                                    'profile_photo_url': review.get('profile_photo_url', 'N/A'),
                                    'relative_time_description': review.get('relative_time_description', 'N/A')
                                } for review in reviews]
                            else:
                                place_info['reviews'] = []
                            
                            places.append(place_info)
                            total_results += 1
                            logging.info(f"Đã tìm thấy: {place_info['name']} (Tổng số: {total_results}/{max_results_per_type})")
                            
                        except Exception as e:
                            logging.error(f"Lỗi khi lấy thông tin chi tiết: {str(e)}")
                            continue
                    
                    # Kiểm tra xem có trang tiếp theo không
                    next_page_token = places_result.get('next_page_token')
                    if not next_page_token:
                        break
                        
                    # Đợi một chút trước khi lấy trang tiếp theo (theo yêu cầu của Google)
                    time.sleep(2)
                    
                except Exception as e:
                    logging.error(f"Lỗi khi tìm kiếm địa điểm: {str(e)}")
                    if retry_count < max_retries:
                        retry_count += 1
                        logging.info(f"Thử lại lần {retry_count}/{max_retries} sau {retry_delay} giây...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        logging.error("Đã vượt quá số lần thử lại tối đa")
                        break
        
        logging.info(f"Hoàn thành! Tổng số địa điểm tìm thấy: {total_results}")
        return places
        
    except Exception as e:
        logging.error(f"Lỗi: {str(e)}")
        return []

def save_to_files(places, base_filename):
    """
    Lưu dữ liệu vào file JSON trong thư mục tương ứng với type
    """
    if not places:
        return
        
    # Lấy type từ places đầu tiên
    place_type = places[0]['type']
    
    # Tạo thư mục output cho type nếu chưa tồn tại
    output_dir = os.path.join('output', place_type)
    os.makedirs(output_dir, exist_ok=True)
    
    # Tạo tên file dựa trên location và timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{base_filename}_{timestamp}.json"
    
    # Lưu dữ liệu vào JSON
    with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
        json.dump(places, f, ensure_ascii=False, indent=2)
    
    logging.info(f"\nĐã lưu dữ liệu vào {os.path.join(output_dir, filename)}")

def process_query(args, query):
    """Process a single query with the given arguments"""
    logging.info(f"Processing query: {query}")
    places = search_places(
        query=query,
        location=args.location,
        radius=args.radius,
        max_results_per_type=args.max_results_per_type
    )
    
    if places:
        save_to_files(places, f"{query.replace(' ', '_')}_{args.location.replace(' ', '_')}")
    else:
        logging.warning(f"No results found for query: {query}")

def main():
    parser = argparse.ArgumentParser(description='Crawl Google Maps data')
    parser.add_argument('--location', type=str, default="Hà Nội, Việt Nam",
                      help='Location to search in (default: Hà Nội, Việt Nam)')
    parser.add_argument('--radius', type=int, default=5000,
                      help='Search radius in meters (default: 5000)')
    parser.add_argument('--queries', type=str, nargs='+',
                      default=['nhà hàng', 'quán ăn', 'nhà hàng sang trọng', 'nhà hàng gia đình', 'quán ăn vặt', 
                               'cafe', 'quán cafe ngon', 'quán cà phê view đẹp', 
                               'khách sạn', 'khách sạn 5 sao', 'resort', 'homestay', 
                               'địa điểm vui chơi', 'công viên', 'trung tâm thương mại', 'spa'],
                      help='List of queries to search for')
    parser.add_argument('--threads', type=int, default=2,
                      help='Number of parallel threads (default: 2)')
    parser.add_argument('--max-results-per-type', type=int, default=1500,
                      help='Maximum number of results per type (default: 1500)')
    parser.add_argument('--max-photos', type=int, default=5,
                      help='Maximum number of photos per place (default: 5)')
    parser.add_argument('--max-api-calls', type=int, default=1000,
                      help='Maximum number of API calls to make (default: 1000)')
    
    args = parser.parse_args()
    
    # Set max API quota
    global MAX_DAILY_QUOTA
    MAX_DAILY_QUOTA = args.max_api_calls
    
    # Process queries in parallel
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(process_query, args, query) for query in args.queries]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing query: {str(e)}")

if __name__ == "__main__":
    main() 