import googlemaps
import json
import time
from datetime import datetime
import pandas as pd
import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

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

def get_city_centers(location):
    """
    Lấy danh sách các trung tâm tìm kiếm trong thành phố
    """
    try:
        # Lấy tọa độ trung tâm thành phố
        geocode_result = gmaps.geocode(location)
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
        place_details_delay = 5  # seconds between place details requests
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
                            
                            # Lấy thông tin chi tiết của địa điểm
                            place_details = gmaps.place(
                                place['place_id'],
                                language='vi',
                                fields=['name', 'formatted_address', 'formatted_phone_number', 
                                       'rating', 'user_ratings_total', 'opening_hours', 
                                       'price_level', 'website']
                            )['result']
                            
                            last_place_details_time = time.time()
                            
                            # Xác định type dựa trên query
                            place_type = query.lower()
                            
                            # Tạo dictionary chứa thông tin địa điểm
                            place_info = {
                                'name': place_details.get('name', 'N/A'),
                                'address': place_details.get('formatted_address', 'N/A'),
                                'phone': place_details.get('formatted_phone_number', 'N/A'),
                                'rating': place_details.get('rating', 'N/A'),
                                'total_ratings': place_details.get('user_ratings_total', 'N/A'),
                                'price_level': place_details.get('price_level', 'N/A'),
                                'website': place_details.get('website', 'N/A'),
                                'type': place_type,
                                'place_id': place['place_id']  # Lưu place_id để tránh trùng lặp
                            }
                            
                            # Thêm giờ mở cửa nếu có
                            if 'opening_hours' in place_details:
                                place_info['opening_hours'] = place_details['opening_hours'].get('weekday_text', [])
                            else:
                                place_info['opening_hours'] = []
                            
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
                      default=['nhà hàng', 'cafe', 'khách sạn', 'địa điểm vui chơi'],
                      help='List of queries to search for')
    parser.add_argument('--threads', type=int, default=2,
                      help='Number of parallel threads (default: 2)')
    parser.add_argument('--max-results-per-type', type=int, default=1500,
                      help='Maximum number of results per type (default: 1500)')
    
    args = parser.parse_args()
    
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