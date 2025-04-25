import os
import pandas as pd
from pathlib import Path

# Đường dẫn đến folder chứa các file CSV
data_dir = Path('/Users/doa_ai/Developer/Grab-project/ai/crawl/crawl_booking_web/script/data_hotels/data_hotels')

# Lấy danh sách tất cả file CSV trong folder
csv_files = list(data_dir.glob('*.csv'))

if not csv_files:
    print("Không tìm thấy file CSV nào trong folder")
    exit()

print(f"Tìm thấy {len(csv_files)} file CSV")

# Tạo DataFrame rỗng để merge
merged_df = pd.DataFrame()

# Đọc và merge từng file
for csv_file in csv_files:
    try:
        print(f"Đang đọc file: {csv_file.name}")
        df = pd.read_csv(csv_file)
        merged_df = pd.concat([merged_df, df], ignore_index=True)
        print(f"Đã merge {len(df)} dòng từ {csv_file.name}")
    except Exception as e:
        print(f"Lỗi khi đọc file {csv_file.name}: {e}")

# Lưu file kết quả
output_file = data_dir / 'merged_hotels.csv'
merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\nĐã merge thành công {len(merged_df)} dòng vào file: {output_file}") 