import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_auth_headers():
    """Get authentication headers from a real browser session"""
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
        "Connection": "keep-alive",
        "X-Foody-Access-Token": "2c4fb2b4-aec5-11ee-b394-8ac29577e80e",  # Cần thay bằng token thật
        "X-Foody-Api-Version": "1",
        "X-Foody-App-Type": "1004",
        "X-Foody-Client-Id": "2c4fb2b4-aec5-11ee-b394-8ac29577e80e",    # Cần thay bằng ID thật
        "X-Foody-Client-Language": "vi",
        "X-Foody-Client-Type": "1",
        "X-Foody-Client-Version": "3.0.0",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

def get_auth_cookies():
    """Get authentication cookies from a real browser session"""
    return {
        "_deliverynow_app_type": "1004",
        "_deliverynow_session": "0wewe23tlzdizds5wtv3fjzm",  # Cần thay bằng session ID thật
        "_gid": "GA1.2.895401915.1744951716",
        "_ga": "GA1.2.596913602.1742658375",
        "_fbp": "fb.1.1742658375215.889272513221187554"
    }

def test_get_summary(restaurant_id: str):
    """Test GetSummaryNew API endpoint"""
    url = "https://gappapi.deliverynow.vn/api/delivery/get_detail"
    
    try:
        logging.info(f"Testing GetSummaryNew API for restaurant {restaurant_id}")
        response = requests.get(
            url, 
            headers=get_auth_headers(),
            cookies=get_auth_cookies(),
            params={
                "id_type": "1",
                "request_id": restaurant_id
            }
        )
        
        logging.info(f"Response Status: {response.status_code}")
        logging.info(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Response Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            logging.error(f"Error response: {response.text}")
            
    except Exception as e:
        logging.error(f"Error testing GetSummaryNew API: {str(e)}")

def test_get_delivery_dishes(restaurant_id: str):
    """Test get_delivery_dishes API endpoint"""
    url = "https://gappapi.deliverynow.vn/api/dish/get_delivery_dishes"
    
    try:
        logging.info(f"Testing get_delivery_dishes API for restaurant {restaurant_id}")
        response = requests.get(
            url,
            headers=get_auth_headers(),
            cookies=get_auth_cookies(),
            params={
                "id_type": "1",
                "request_id": restaurant_id
            }
        )
        
        logging.info(f"Response Status: {response.status_code}")
        logging.info(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Response Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            logging.error(f"Error response: {response.text}")
            
    except Exception as e:
        logging.error(f"Error testing get_delivery_dishes API: {str(e)}")

if __name__ == "__main__":
    # Test restaurant ID from your screenshot
    restaurant_id = "732773"
    
    # Test both APIs
    test_get_summary(restaurant_id)
    print("\n" + "="*80 + "\n")
    test_get_delivery_dishes(restaurant_id) 