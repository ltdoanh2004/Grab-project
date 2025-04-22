import json
import pandas as pd

# Danh sách đường dẫn đến các file JSON cần merge
list_path = [
    '/Users/doa_ai/Developer/Grab-project/ai/crawl_booking_web/data_hotels/data_hotels_test_page68_20250422_152300.json',
    '/Users/doa_ai/Developer/Grab-project/ai/crawl_booking_web/data_hotels/data_hotels_test_page367_20250422_152032.json',
    '/Users/doa_ai/Developer/Grab-project/ai/crawl_booking_web/data_hotels/data_hotels_test_page267_20250422_152026.json',
    '/Users/doa_ai/Developer/Grab-project/ai/crawl_booking_web/data_hotels/data_hotels_test_page166_20250422_152042.json'
]

merged_data = []

for path in list_path:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Nếu data là list: append từng item
            if isinstance(data, list):
                merged_data.extend(data)

            # Nếu data là dict, kiểm tra nếu có key 'hotels' hoặc lấy toàn bộ
            elif isinstance(data, dict):
                if 'hotels' in data and isinstance(data['hotels'], list):
                    merged_data.extend(data['hotels'])
                else:
                    merged_data.append(data)
            else:
                print(f"⚠️ Không hỗ trợ định dạng trong file: {path}")

    except Exception as e:
        print(f"❌ Lỗi đọc {path}: {e}")

# Ghi ra CSV nếu có dữ liệu
if merged_data:
    df = pd.DataFrame(merged_data)
    df.to_csv('/Users/doa_ai/Developer/Grab-project/ai/crawl_booking_web/hotels_data_from_bookingweb.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Đã merge {len(list_path)} file → hotels_data_from_bookingweb.csv ({len(df)} dòng)")
else:
    print("⚠️ Không có dữ liệu để ghi.")
