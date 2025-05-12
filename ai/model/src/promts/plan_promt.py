JSON_SCHEMA_EXAMPLE = {
    "trip_name": "<string – ex: Đà Nẵng nghỉ dưỡng 4 ngày>",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "user_id": "<string>",
    "destination": "<string>",
    "plan_by_day": [
        {
            "date": "YYYY-MM-DD",
            "day_title": "Ngày 1: Khám phá biển",
            "segments": [
                {
                    "time_of_day": "morning",
                    "activities": [
                        {
                            "id": "<string>",
                            "type": "accommodation | place | restaurant",
                            "name": "<string>",
                            "start_time": "HH:MM",
                            "end_time": "HH:MM",
                            "description": "<string>",
                            "location": "<string>",
                            "rating": "<number>",
                            "price": "<number or string>",
                            "image_url": "<string>",
                            "url": "<string>"
                        }
                    ]
                },
                {
                    "time_of_day": "afternoon",
                    "activities": [
                        {
                            "id": "<string>",
                            "type": "place",
                            "name": "<string>",
                            "start_time": "HH:MM",
                            "end_time": "HH:MM",
                            "description": "<string>",
                            "location": "<string>",
                            "rating": "<number>",
                            "price": "<number or string>",
                            "image_url": "<string>",
                            "url": "<string>"
                        }
                    ]
                }
            ]
        },
        {
            "date": "YYYY-MM-DD",
            "day_title": "Ngày 2: Khám phá núi",
            "segments": [
                {
                    "time_of_day": "morning",
                    "activities": [
                        {
                            "id": "<string>",
                            "type": "place",
                            "name": "<string>",
                            "start_time": "HH:MM",
                            "end_time": "HH:MM",
                            "description": "<string>",
                            "location": "<string>",
                            "rating": "<number>",
                            "price": "<number or string>",
                            "image_url": "<string>",
                            "url": "<string>"
                        }
                    ]
                }
            ]
        },
        {
            "date": "YYYY-MM-DD",
            "day_title": "Ngày 3: Khám phá ẩm thực",
            "segments": [
                {
                    "time_of_day": "morning",
                    "activities": [
                        {
                            "id": "<string>",
                            "type": "restaurant",
                            "name": "<string>",
                            "start_time": "HH:MM",
                            "end_time": "HH:MM",
                            "description": "<string>",
                            "location": "<string>",
                            "rating": "<number>",
                            "price": "<number or string>",
                            "image_url": "<string>",
                            "url": "<string>"
                        }
                    ]
                }
            ]
        }
    ]
}

system_plan_prompt = """
            Chuyên gia lập kế hoạch du lịch Việt Nam. Tạo lịch trình hấp dẫn dưới dạng JSON.
            
            CHÚ Ý QUAN TRỌNG:
            1. CHỈ TRẢ VỀ JSON THUẦN TÚY! KHÔNG THÊM BẤT KỲ VĂN BẢN NÀO TRƯỚC HOẶC SAU JSON!
            2. PHẢN HỒI CỦA BẠN PHẢI BẮT ĐẦU BẰNG DẤU "{" VÀ KẾT THÚC BẰNG DẤU "}" - KHÔNG CÓ GÌ KHÁC!
            3. PHẢI ĐẢM BẢO JSON KHÔNG BỊ CẮT NGẮN - TẤT CẢ CÁC DẤU NGOẶC PHẢI ĐƯỢC ĐÓNG ĐÚNG CÁCH!
            4. MÔ TẢ HOẠT ĐỘNG NÊN NGẮN GỌN (<100 ký tự) VÀ TẬP TRUNG VÀO TRẢI NGHIỆM
            5. TẤT CẢ CÁC TRƯỜNG TRONG JSON PHẢI CÓ GIÁ TRỊ, KHÔNG ĐƯỢC ĐỂ TRỐNG
            
            Yêu cầu:
            1. Ưu tiên khách sạn đầu tiên. Mỗi chuyến đi chỉ nên có 1 khách sạn.
            2. Mô tả hấp dẫn và sinh động (2-3 câu NGẮN GỌN), với giọng hướng dẫn viên: "Bạn sẽ được...", "Chúng ta sẽ..."
            3. Tiêu đề ngày sáng tạo (vd: "Ngày 1: Hành trình khám phá thiên đường biển xanh")
            4. Mỗi segment (morning/afternoon/evening) có 4-5 hoạt động
            5. Ưu tiên chọn những địa điểm cụ thể, ít lấy từ tour lại
            6. Tuân thủ chính xác cấu trúc JSON yêu cầu
            7. Sử dụng đúng ID từ dữ liệu đầu vào
"""