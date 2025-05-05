"""
Key points
-----------
* `JSON_SCHEMA_EXAMPLE` holds a *minimal* skeleton of the structure and
  is embedded straight into the prompt.
* `JsonOutputParser` (LangChain) post‑validates the LLM response and
  returns a native Python dict you can hand to FE / persist to DB.
* A helper `TravelPlanner.generate_plan` takes the consolidated
  `input_data = {"accommodations": [...], "places": [...], "restaurants": [...]}`.
  + You can optionally pass `trip_name`, `start_date`, `end_date`, `user_id`.
* Ready stubs (`WeatherTool`, `MapTool`) illustrate cách add tools sau
  này – chỉ cần bổ sung `func` thật và liệt kê vào `TOOLS`.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional
import time

from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.chat_models import ChatOpenAI

from utils.utils import save_data_to_json
# ---------------------------------------------------------------------------
# 🔧 ENV & Logging
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
print(ROOT)
load_dotenv(ROOT / ".env")

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
log = logging.getLogger("travel_planner")

# ---------------------------------------------------------------------------
# 📜 Example JSON schema we expect from LLM
# ---------------------------------------------------------------------------
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

FORMAT_INSTRUCTIONS = (
    "Respond ONLY with VALID minified JSON (no markdown) that matches "
    "exactly the structure & keys of the following example: "
    f"{json.dumps(JSON_SCHEMA_EXAMPLE, ensure_ascii=False)}"
)

json_parser = JsonOutputParser()

# ---------------------------------------------------------------------------
# 🛠️  Optional tools stubs – plug real API later
# ---------------------------------------------------------------------------

def dummy_weather_tool(query: str) -> str:  # pragma: no cover
    """Placeholder weather tool."""
    return "{\"temp\":30, \"condition\":\"sunny\"}"

TOOLS: List[Tool] = [
    Tool(name="weather", func=dummy_weather_tool, description="Lấy dữ liệu thời tiết"),
]

# ---------------------------------------------------------------------------
# 🚂  Planner class
# ---------------------------------------------------------------------------


class PlanModel:
    def __init__(self, temperature: float = 0.7):
        self.llm = OpenAI(api_key=os.getenv("OPEN_API_KEY"), temperature=temperature)
        self.parser = json_parser  # langchain JSON parser

    # ---------------------------------------------------------------------
    # 🔑 Prompt builder
    # ---------------------------------------------------------------------
    def _build_prompt(self) -> PromptTemplate:
        template = (
            "You are an expert Vietnamese travel planner. Using the user data, "
            "generate a coherent multi‑day trip strictly in JSON format.\n\n"
            "IMPORTANT: Your response MUST be ONLY VALID JSON. "
            "Do NOT include any text before or after the JSON. "
            "Do NOT add title, notes, or explanations.\n\n"
            "User context (JSON): {user_json}\n\n" + FORMAT_INSTRUCTIONS
        )
        # Specify the input variables explicitly
        return PromptTemplate(template=template, input_variables=["user_json"])

    # ------------------------------------------------------------------
    # 🧩  Plain chain (no external tools)
    # ------------------------------------------------------------------
    def generate_plan(self, input_data: Dict[str, Any], **meta: Any) -> Dict[str, Any]:
        """LLM only – returns parsed JSON dict."""
        log.info("Generating plan (no agent)…")
        
        try:
            merged_data = {**input_data, **meta}
            
            if "trip_name" not in merged_data:
                merged_data["trip_name"] = "Trip to " + merged_data.get("destination", "Unknown")
            
            try:
                from datetime import datetime, timedelta
                
                if not merged_data.get('start_date'):
                    start_date = datetime.now()
                    merged_data['start_date'] = start_date.strftime("%Y-%m-%d")
                else:
                    start_date = datetime.strptime(merged_data['start_date'], "%Y-%m-%d")
                
                if not merged_data.get('end_date'):
                    end_date = start_date + timedelta(days=2)  # Default 3-day trip
                    merged_data['end_date'] = end_date.strftime("%Y-%m-%d")
                else:
                    end_date = datetime.strptime(merged_data['end_date'], "%Y-%m-%d")
                
                num_days = (end_date - start_date).days + 1
                if num_days < 1:
                    num_days = 1
                    end_date = start_date
                    merged_data['end_date'] = end_date.strftime("%Y-%m-%d")
            except Exception as date_error:
                log.warning(f"Date parsing error: {date_error}. Using default dates.")
                from datetime import datetime, timedelta
                num_days = 3
                start_date = datetime.now()
                end_date = start_date + timedelta(days=num_days-1)
                merged_data['start_date'] = start_date.strftime("%Y-%m-%d")
                merged_data['end_date'] = end_date.strftime("%Y-%m-%d")
            
            final_plan = {
                "trip_name": merged_data.get("trip_name", "Trip to " + merged_data.get("destination", "Unknown")),
                "start_date": merged_data.get("start_date"),
                "end_date": merged_data.get("end_date"),
                "user_id": merged_data.get("user_id", "user123"),
                "destination": merged_data.get("destination", "Unknown"),
                "plan_by_day": []
            }
            
            # System prompt for more control
            system_prompt = """
            Chuyên gia lập kế hoạch du lịch Việt Nam. Tạo lịch trình hấp dẫn dưới dạng JSON.
            
            CHÚ Ý QUAN TRỌNG: CHỈ TRẢ VỀ JSON THUẦN TÚY! KHÔNG THÊM BẤT KỲ VĂN BẢN NÀO TRƯỚC HOẶC SAU JSON!
            PHẢN HỒI CỦA BẠN PHẢI BẮT ĐẦU BẰNG DẤU "{" VÀ KẾT THÚC BẰNG DẤU "}" - KHÔNG CÓ GÌ KHÁC!
            
            Yêu cầu:
            1. Ưu tiên khách sạn đầu tiên
            2. Mô tả hấp dẫn và sinh động (3-4 câu), với giọng hướng dẫn viên: "Bạn sẽ được...", "Chúng ta sẽ..."
            3. Tiêu đề ngày sáng tạo (vd: "Ngày 1: Hành trình khám phá thiên đường biển xanh")
            4. Mỗi segment (morning/afternoon/evening) có 2-3 hoạt động gần nhau
            5. Tuân thủ chính xác cấu trúc JSON yêu cầu
            6. Sử dụng đúng ID từ dữ liệu đầu vào
            """
            
            for day_num in range(num_days):
                current_date = start_date + timedelta(days=day_num)
                current_date_str = current_date.strftime("%Y-%m-%d")
                
                day_title = f"Ngày {day_num+1}: "
                if day_num == 0:
                    day_title += "Khám phá biển"
                elif day_num == 1:
                    day_title += "Khám phá núi"
                elif day_num == 2:
                    day_title += "Khám phá văn hóa"
                else:
                    day_title += "Khám phá địa phương"
                
                # Create prompt for this specific day with simplified structure
                day_prompt = f"""
                Tạo chi tiết cho ngày {day_num+1} (ngày {current_date_str}) của lịch trình du lịch {merged_data.get("destination")}.
                Tạo 3 segments (morning, afternoon, evening) với các hoạt động phù hợp.
                
                CHÚ Ý QUAN TRỌNG: CHỈ TRẢ VỀ JSON THUẦN TÚY! KHÔNG THÊM BẤT KỲ VĂN BẢN NÀO TRƯỚC HOẶC SAU JSON!
                PHẢN HỒI CỦA BẠN PHẢI BẮT ĐẦU BẰNG DẤU "{" VÀ KẾT THÚC BẰNG DẤU "}" - KHÔNG CÓ GÌ KHÁC!
                
                Thông tin chuyến đi:
                Điểm đến: {merged_data.get("destination")}
                Khách sạn: {[(acc.get("name", ""), acc.get("accommodation_id", "")) for acc in merged_data.get("accommodations", [])]}
                Địa điểm: {[(place.get("name", ""), place.get("place_id", "")) for place in merged_data.get("places", [])]}
                Nhà hàng: {[(rest.get("name", ""), rest.get("restaurant_id", "")) for rest in merged_data.get("restaurants", [])]}
                
                Cấu trúc JSON cần tuân thủ:
                {{
                    "date": "{current_date_str}",
                    "day_title": "Ngày {day_num+1}: [Tiêu đề sáng tạo và độc đáo]",
                    "segments": [...]
                }}
                
                Hướng dẫn quan trọng:
                - Tiêu đề ngày PHẢI sáng tạo, hấp dẫn và ĐA DẠNG (vd: "Hành trình khám phá thiên đường...", "Đắm mình trong văn hóa...", "Khám phá ẩm thực đặc sắc...")
                - Mô tả phải sống động với phong cách hướng dẫn viên: "Bạn sẽ được...", "Hãy cùng khám phá..."
                - Luôn sử dụng đúng ID từ dữ liệu đầu vào
                - Mỗi segment (morning/afternoon/evening) BẮT BUỘC phải có 2-3 hoạt động gần nhau, KHÔNG được chỉ có 1 hoạt động
                - Phân bổ các địa điểm tham quan và nhà hàng hợp lý trong các segment
                """
                
                # Điều chỉnh prompt dựa vào day_num (nếu là ngày đầu tiên, hiển thị khách sạn là activity đầu tiên)
                if day_num == 0:
                    day_prompt += f"""
                                {{
                                    "id": "{merged_data.get('accommodations', [{}])[0].get('accommodation_id', 'hotel_morning_day' + str(day_num+1)) if merged_data.get('accommodations') else 'hotel_morning_day' + str(day_num+1)}",
                                    "type": "accommodation",
                                    "name": "Tên khách sạn",
                                    "start_time": "08:00",
                                    "end_time": "10:00",
                                    "description": "Mô tả ngắn",
                                    "location": "Địa chỉ đầy đủ",
                                    "booking_link": "https://...",
                                    "room_info": "Thông tin phòng",
                                    "tax_info": "Thông tin thuế",
                                    "elderly_friendly": true,
                                    "rating": 4.5,
                                    "price": 850000,
                                    "image_url": "",
                                    "url": ""
                                }},"""
                
                day_prompt += f"""
                                {{
                                    "id": "{merged_data.get('places', [{}])[0].get('place_id', 'place_morning_day' + str(day_num+1)) if merged_data.get('places') else 'place_morning_day' + str(day_num+1)}",
                                    "type": "place",
                                    "name": "Tên địa điểm",
                                    "start_time": "08:00",
                                    "end_time": "10:00",
                                    "description": "Mô tả ngắn",
                                    "address": "Địa chỉ đầy đủ",
                                    "categories": "sightseeing",
                                    "duration": "2h",
                                    "opening_hours": "08:00-17:00",
                                    "rating": 4.5,
                                    "price": 50000,
                                    "image_url": "",
                                    "url": ""
                                }},
                                {{
                                    "id": "{merged_data.get('restaurants', [{}])[min(0, len(merged_data.get('restaurants', []))-1)].get('restaurant_id', 'restaurant_morning_day' + str(day_num+1)) if merged_data.get('restaurants') else 'restaurant_morning_day' + str(day_num+1)}",
                                    "type": "restaurant",
                                    "name": "Ăn sáng",
                                    "start_time": "07:00",
                                    "end_time": "08:00",
                                    "description": "Mô tả ngắn",
                                    "address": "Địa chỉ đầy đủ", 
                                    "cuisines": "Ẩm thực địa phương",
                                    "price_range": "50,000-100,000 VND",
                                    "rating": 4.5,
                                    "phone": "0123456789",
                                    "services": ["đặt bàn", "giao hàng"],
                                    "image_url": "",
                                    "url": ""
                                }}
                            ]
                        }},
                        {{
                            "time_of_day": "afternoon",
                            "activities": [
                                {{
                                    "id": "{merged_data.get('places', [{}])[min(2, len(merged_data.get('places', []))-1)].get('place_id', 'place_afternoon_day' + str(day_num+1)) if len(merged_data.get('places', [])) > 2 else 'place_afternoon_day' + str(day_num+1)}",
                                    "type": "place",
                                    "name": "Tên địa điểm",
                                    "start_time": "13:00",
                                    "end_time": "15:00",
                                    "description": "Mô tả ngắn",
                                    "address": "Địa chỉ đầy đủ",
                                    "categories": "sightseeing",
                                    "duration": "2h",
                                    "opening_hours": "08:00-17:00",
                                    "rating": 4.5,
                                    "price": 50000,
                                    "image_url": "",
                                    "url": ""
                                }},
                                {{
                                    "id": "{merged_data.get('places', [{}])[min(3, len(merged_data.get('places', []))-1)].get('place_id', 'place_afternoon2_day' + str(day_num+1)) if len(merged_data.get('places', [])) > 3 else 'place_afternoon2_day' + str(day_num+1)}",
                                    "type": "place",
                                    "name": "Tên địa điểm thứ 2",
                                    "start_time": "15:30",
                                    "end_time": "17:00",
                                    "description": "Mô tả ngắn",
                                    "address": "Địa chỉ đầy đủ",
                                    "categories": "sightseeing",
                                    "duration": "1h30m",
                                    "opening_hours": "08:00-17:00",
                                    "rating": 4.5,
                                    "price": 50000,
                                    "image_url": "",
                                    "url": ""
                                }},
                                {{
                                    "id": "{merged_data.get('restaurants', [{}])[min(1, len(merged_data.get('restaurants', []))-1)].get('restaurant_id', 'restaurant_afternoon_day' + str(day_num+1)) if len(merged_data.get('restaurants', [])) > 1 else merged_data.get('restaurants', [{}])[0].get('restaurant_id', 'restaurant_afternoon_day' + str(day_num+1)) if merged_data.get('restaurants') else 'restaurant_afternoon_day' + str(day_num+1)}",
                                    "type": "restaurant",
                                    "name": "Ăn trưa",
                                    "start_time": "12:00",
                                    "end_time": "13:00",
                                    "description": "Mô tả ngắn",
                                    "address": "Địa chỉ đầy đủ", 
                                    "cuisines": "Hải sản, Đặc sản địa phương",
                                    "price_range": "100,000-300,000 VND",
                                    "rating": 4.5,
                                    "phone": "0123456789",
                                    "services": ["đặt bàn", "giao hàng"],
                                    "image_url": "",
                                    "url": ""
                                }}
                            ]
                        }},
                        {{
                            "time_of_day": "evening",
                            "activities": [
                                {{
                                    "id": "{merged_data.get('places', [{}])[min(4, len(merged_data.get('places', []))-1)].get('place_id', 'place_evening_day' + str(day_num+1)) if len(merged_data.get('places', [])) > 4 else 'place_evening_day' + str(day_num+1)}",
                                    "type": "place",
                                    "name": "Địa điểm buổi tối",
                                    "start_time": "18:00",
                                    "end_time": "19:00",
                                    "description": "Mô tả ngắn",
                                    "address": "Địa chỉ đầy đủ",
                                    "categories": "sightseeing",
                                    "duration": "1h",
                                    "opening_hours": "08:00-21:00",
                                    "rating": 4.5,
                                    "price": 50000,
                                    "image_url": "",
                                    "url": ""
                                }},
                                {{
                                    "id": "{merged_data.get('places', [{}])[min(5, len(merged_data.get('places', []))-1)].get('place_id', 'place_evening2_day' + str(day_num+1)) if len(merged_data.get('places', [])) > 5 else 'place_evening2_day' + str(day_num+1)}",
                                    "type": "place",
                                    "name": "Địa điểm thứ 2 buổi tối",
                                    "start_time": "19:30",
                                    "end_time": "20:30",
                                    "description": "Mô tả ngắn",
                                    "address": "Địa chỉ đầy đủ",
                                    "categories": "entertainment",
                                    "duration": "1h",
                                    "opening_hours": "18:00-23:00",
                                    "rating": 4.5,
                                    "price": 50000,
                                    "image_url": "",
                                    "url": ""
                                }},
                                {{
                                    "id": "{merged_data.get('restaurants', [{}])[min(2, len(merged_data.get('restaurants', []))-1)].get('restaurant_id', 'restaurant_evening_day' + str(day_num+1)) if len(merged_data.get('restaurants', [])) > 2 else merged_data.get('restaurants', [{}])[0].get('restaurant_id', 'restaurant_evening_day' + str(day_num+1)) if merged_data.get('restaurants') else 'restaurant_evening_day' + str(day_num+1)}",
                                    "type": "restaurant",
                                    "name": "Nhà hàng tối",
                                    "start_time": "20:30",
                                    "end_time": "22:30",
                                    "description": "Mô tả ngắn",
                                    "address": "Địa chỉ đầy đủ", 
                                    "cuisines": "Hải sản, Đặc sản địa phương",
                                    "price_range": "100,000-300,000 VND",
                                    "rating": 4.5,
                                    "phone": "0123456789",
                                    "services": ["đặt bàn", "giao hàng"],
                                    "image_url": "",
                                    "url": ""
                                }}
                            ]
                        }}
                    ]
                }}
                
                Hãy chuẩn hóa định dạng dữ liệu theo TYPE của activity:
                1. Nếu type là "accommodation":
                   - Bổ sung: "booking_link", "room_info", "tax_info", "elderly_friendly"
                   - Đổi "address" thành "location"
                   - Price nên là số nguyên (VND)
                   - Sử dụng ID từ danh sách accommodation_id cung cấp (hotel_XXXXX)
                
                2. Nếu type là "place":
                   - Bổ sung: "categories", "duration", "opening_hours"
                   - Giữ nguyên "address"
                   - Price là số nguyên nếu có (VND)
                   - Sử dụng ID từ danh sách place_id cung cấp (place_XXXXX)
                
                3. Nếu type là "restaurant":
                   - Bổ sung: "cuisines", "price_range", "phone", "services" (array)
                   - Giữ nguyên "address"
                   - Sử dụng ID từ danh sách restaurant_id cung cấp (restaurant_XXXXX)
                
                QUAN TRỌNG:
                - LUÔN LUÔN sử dụng ID từ dữ liệu đầu vào (accommodation_id, place_id, restaurant_id)
                - Không tạo ID tùy ý mà phải dùng những ID đã được cung cấp trong dữ liệu
                - Mỗi SEGMENT (morning, afternoon, evening) CÓ THỂ có NHIỀU ACTIVITIES (2-3 activities mỗi segment)
                - Các activities trong cùng một segment nên có mối liên hệ về địa lý (gần nhau) và thời gian (liền mạch)
                - Nếu description có trong dữ liệu đầu vào, HÃY SỬ DỤNG description đó, và thêm giọng văn hướng dẫn viên du lịch (vd: "Bạn sẽ được...", "Chúng ta sẽ...", "Hãy cùng khám phá...")
                - Chỉ trả về đối tượng JSON hợp lệ, không viết gì thêm.
                - You must choose for the user the hotel first, to make sure that they can have a suitable hotel. If the next activities is far from the chosen hotel, you must choose another hotel and update the hotel in the itinerary, but you should rarely change the hotel.
                """
                
                # Thêm hướng dẫn về day_title và description cho day_prompt 
                day_prompt += """
                
                HƯỚNG DẪN QUAN TRỌNG VỀ TIÊU ĐỀ VÀ MÔ TẢ:
                
                "Bạn sẽ được đắm mình trong làn nước biển trong vắt, nơi sóng nhẹ vỗ về bờ cát trắng mịn. Hãy để gió biển mát lành vuốt ve làn da và lắng nghe tiếng sóng rì rào như nhạc thiên nhiên. Chúng ta sẽ cùng khám phá những góc nhỏ tuyệt đẹp để lưu giữ kỷ niệm đáng nhớ."
                """
                
                # Thêm ví dụ ngắn gọn về mô tả tốt
                day_prompt += """
                
                MẪU: "Bạn sẽ được khám phá..."
                """
                
                # Thêm mẫu ngắn gọn cho day_prompt 
                day_prompt += """
                
                MẪU: "Bạn sẽ được đắm mình trong làn nước biển trong vắt, nơi sóng nhẹ vỗ về bờ cát trắng mịn."
                """
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": day_prompt}
                ]
                
                day_response = self.llm.invoke(messages)
                
                # Lấy nội dung từ day_response
                day_response_content = day_response.content if hasattr(day_response, 'content') else day_response
                
                # Chuẩn hóa kết quả trước khi parse
                day_response_content = self._cleanup_llm_response(day_response_content)
                
                try:
                    try:
                        day_data = self.parser.parse(day_response_content)
                    except Exception as json_error:
                        log.warning(f"Initial JSON parsing failed: {json_error}. Attempting to extract JSON.")
                        import re
                        import json
                        
                        cleaned_response = re.sub(r'^(System:|User:|Assistant:|Day \d+:|Ngày \d+:)[^\{]*', '', day_response_content.strip())
                        
                        json_match = re.search(r'(\{[\s\S]*\})', cleaned_response)
                        
                        if json_match:
                            potential_json = json_match.group(1)
                            
                            try:
                                day_data = json.loads(potential_json)
                            except json.JSONDecodeError:
                                try:
                                    open_braces = potential_json.count('{')
                                    closed_braces = potential_json.count('}')
                                    
                                    fixed_json = potential_json
                                    if open_braces > closed_braces:
                                        fixed_json += '}' * (open_braces - closed_braces)
                                    
                                    fixed_json = re.sub(r',(\s*[}\]])', r'\1', fixed_json)
                                    
                                    fixed_json = re.sub(r'([^\\])"([^"]*?)([^\\])(\s*[}\]])', r'\1"\2\3"\4', fixed_json)
                                    
                                    # Try parsing again
                                    day_data = json.loads(fixed_json)
                                except Exception as repair_error:
                                    log.error(f"Could not repair JSON: {potential_json[:100]}... Error: {repair_error}")
                                    raise ValueError("Could not extract valid JSON after repair attempts")
                        else:
                            log.error("No JSON-like content found in response. Creating basic structure.")
                            day_data = {
                                "date": current_date_str,
                                "day_title": f"Ngày {day_num+1}: Khám phá",
                                "segments": [
                                    {"time_of_day": "morning", "activities": []},
                                    {"time_of_day": "afternoon", "activities": []},
                                    {"time_of_day": "evening", "activities": []}
                                ]
                            }
                    
                    if "segments" not in day_data or not day_data["segments"]:
                        day_data["segments"] = []
                    
                    existing_segments = {segment.get("time_of_day"): segment for segment in day_data["segments"]}
                    
                    # Check for required segments and add if missing
                    for required_segment in ["morning", "afternoon", "evening"]:
                        if required_segment not in existing_segments:
                            # Define a helper function to extract image URL from various formats
                            def extract_image_url(item):
                                # Check if there's a direct image_url string
                                if isinstance(item.get("image_url"), str) and item.get("image_url"):
                                    return item.get("image_url")
                                
                                # Check alternative direct image fields
                                if isinstance(item.get("imageUrl"), str) and item.get("imageUrl"):
                                    return item.get("imageUrl")
                                if isinstance(item.get("image"), str) and item.get("image"):
                                    return item.get("image")
                                
                                # Check for array-based image fields
                                for field in ["image_url", "imageUrl", "image", "images"]:
                                    # If the field exists and is a list/array
                                    if isinstance(item.get(field), list) and len(item.get(field)) > 0:
                                        first_image = item.get(field)[0]
                                        # If the item is a string, use it directly
                                        if isinstance(first_image, str):
                                            return first_image
                                        # If the item is a dict with a url field
                                        elif isinstance(first_image, dict) and first_image.get("url"):
                                            return first_image.get("url")
                                
                                # Nothing found
                                return ""

                            if required_segment not in existing_segments:
                                # Create a basic segment with default activity
                                default_activity = {}
                                if required_segment == "morning" and merged_data.get("accommodations"):
                                    # Get accommodation ID first
                                    accommodation_id = merged_data["accommodations"][0].get("accommodation_id", merged_data["accommodations"][0].get("id", f"hotel_morning_day{day_num+1}"))
                                    
                                    # Print all accommodation IDs for debugging
                                    log.info(f"Available accommodation IDs: {[a.get('accommodation_id', a.get('id', 'unknown')) for a in merged_data.get('accommodations', [])]}")
                                    log.info(f"Looking for accommodation ID: {accommodation_id}")
                                    
                                    # Find the matching accommodation to get complete data
                                    matching_accommodation = None
                                    for acc in merged_data.get("accommodations", []):
                                        # Check for exact matches first
                                        if acc.get("accommodation_id") == accommodation_id or acc.get("id") == accommodation_id:
                                            matching_accommodation = acc
                                            log.info(f"Found exact match for accommodation ID: {accommodation_id}")
                                            break
                                        
                                        # If the accommodation_id contains the ID (e.g., "hotel_123" contains "123")
                                        elif accommodation_id and acc.get("accommodation_id") and accommodation_id in acc.get("accommodation_id"):
                                            matching_accommodation = acc
                                            log.info(f"Found partial match: {accommodation_id} in {acc.get('accommodation_id')}")
                                            break
                                        elif accommodation_id and acc.get("id") and accommodation_id in acc.get("id"):
                                            matching_accommodation = acc
                                            log.info(f"Found partial match: {accommodation_id} in {acc.get('id')}")
                                            break
                                    
                                    if not matching_accommodation and merged_data.get("accommodations"):
                                        matching_accommodation = merged_data["accommodations"][0]
                                        log.info(f"No match found, using first accommodation")
                                    
                                    log.info(f"Matched accommodation: {matching_accommodation}")
                                    
                                    image_url = ""
                                    if matching_accommodation:
                                        image_url = extract_image_url(matching_accommodation)
                                        log.info(f"Extracted accommodation image URL: {image_url}")
                                    
                                    original_description = matching_accommodation.get("description", "")
                                    if original_description:
                                        # Sử dụng nội dung từ original_description nhưng để model tự viết lại
                                        # với giọng văn hướng dẫn viên du lịch
                                        key_points = original_description[:200] if len(original_description) > 200 else original_description
                                        description = f"Tại khách sạn tuyệt vời này, bạn sẽ được tận hưởng {key_points.split('.')[0].lower() if '.' in key_points else key_points.lower()}. Hãy nghỉ ngơi và chuẩn bị cho những trải nghiệm tuyệt vời tiếp theo!"
                                    else:
                                        description = "Chúng tôi sẽ đưa bạn đến khách sạn thoải mái này để nghỉ ngơi và chuẩn bị cho hành trình khám phá. Tại đây bạn sẽ được tận hưởng dịch vụ chu đáo và tiện nghi hiện đại."
                                    
                                    default_activity = {
                                        "id": accommodation_id,
                                        "type": "accommodation",
                                        "name": matching_accommodation.get("name", merged_data["accommodations"][0].get("name", "Khách sạn")) if matching_accommodation else merged_data["accommodations"][0].get("name", "Khách sạn"),
                                        "start_time": "08:00",
                                        "end_time": "10:00",
                                        "description": description,
                                        "location": matching_accommodation.get("location", matching_accommodation.get("address", merged_data["accommodations"][0].get("location", merged_data["accommodations"][0].get("address", "")))) if matching_accommodation else merged_data["accommodations"][0].get("location", merged_data["accommodations"][0].get("address", "")),
                                        "rating": float(matching_accommodation.get("rating", merged_data["accommodations"][0].get("rating", 4.5))) if matching_accommodation else float(merged_data["accommodations"][0].get("rating", 4.5)),
                                        "price": float(matching_accommodation.get("price", merged_data["accommodations"][0].get("price", 850000))) if matching_accommodation else float(merged_data["accommodations"][0].get("price", 850000)),
                                        "image_url": image_url,
                                        "booking_link": matching_accommodation.get("booking_link", merged_data["accommodations"][0].get("booking_link", "")) if matching_accommodation else merged_data["accommodations"][0].get("booking_link", ""),
                                        "room_info": matching_accommodation.get("room_info", merged_data["accommodations"][0].get("room_info", "Phòng tiêu chuẩn, 2 giường")) if matching_accommodation else merged_data["accommodations"][0].get("room_info", "Phòng tiêu chuẩn, 2 giường"),
                                        "tax_info": matching_accommodation.get("tax_info", merged_data["accommodations"][0].get("tax_info", "Đã bao gồm thuế VAT")) if matching_accommodation else merged_data["accommodations"][0].get("tax_info", "Đã bao gồm thuế VAT"),
                                        "elderly_friendly": matching_accommodation.get("elderly_friendly", merged_data["accommodations"][0].get("elderly_friendly", True)) if matching_accommodation else merged_data["accommodations"][0].get("elderly_friendly", True),
                                        "url": matching_accommodation.get("url", matching_accommodation.get("link", merged_data["accommodations"][0].get("url", merged_data["accommodations"][0].get("link", "")))) if matching_accommodation else merged_data["accommodations"][0].get("url", merged_data["accommodations"][0].get("link", ""))
                                    }
                                elif required_segment == "afternoon" and merged_data.get("places"):
                                    place_index = min(day_num, len(merged_data["places"])-1) if merged_data["places"] else 0
                                    if place_index >= 0 and merged_data["places"]:
                                        place_id = merged_data["places"][place_index].get("place_id", merged_data["places"][place_index].get("id", f"place_afternoon_day{day_num+1}"))
                                        
                                        log.info(f"Available place IDs: {[p.get('place_id', p.get('id', 'unknown')) for p in merged_data.get('places', [])]}")
                                        log.info(f"Looking for place ID: {place_id}")
                                        
                                        matching_place = None
                                        for place in merged_data.get("places", []):
                                            if place.get("place_id") == place_id or place.get("id") == place_id:
                                                matching_place = place
                                                log.info(f"Found exact match for place ID: {place_id}")
                                                break
                                            
                                            elif place_id and place.get("place_id") and place_id in place.get("place_id"):
                                                matching_place = place
                                                log.info(f"Found partial match: {place_id} in {place.get('place_id')}")
                                                break
                                            elif place_id and place.get("id") and place_id in place.get("id"):
                                                matching_place = place
                                                log.info(f"Found partial match: {place_id} in {place.get('id')}")
                                                break
                                        
                                        if not matching_place:
                                            matching_place = merged_data["places"][place_index]
                                            log.info(f"No match found, using place at index {place_index}")
                                        
                                        # Log the matched place for debugging
                                        log.info(f"Matched place: {matching_place}")
                                        
                                        # Extract image URL
                                        image_url = ""
                                        if matching_place:
                                            image_url = extract_image_url(matching_place)
                                            log.info(f"Extracted place image URL: {image_url}")
                                        
                                        # Process description - add tour guide style narration
                                        original_description = matching_place.get("description", "")
                                        if original_description:
                                            # Sử dụng nội dung từ original_description nhưng để model tự viết lại
                                            # với giọng văn hướng dẫn viên du lịch
                                            key_points = original_description[:200] if len(original_description) > 200 else original_description
                                            description = f"Bạn sẽ được khám phá địa điểm tuyệt vời này, nơi {key_points.split('.')[0].lower() if '.' in key_points else key_points.lower()}. Chúng ta sẽ cùng nhau tìm hiểu về văn hóa và lịch sử độc đáo của nơi đây."
                                        else:
                                            description = "Tham quan địa điểm nổi tiếng này, bạn sẽ được trải nghiệm vẻ đẹp đặc trưng của địa phương và khám phá những nét văn hóa độc đáo không thể bỏ qua."
                                        
                                        default_activity = {
                                            "id": place_id,
                                            "type": "place",
                                            "name": matching_place.get("name", "Địa điểm tham quan"),
                                            "start_time": "14:00",
                                            "end_time": "16:00",
                                            "description": description,
                                            "address": matching_place.get("address", matching_place.get("location", "")),
                                            "categories": matching_place.get("categories", "sightseeing"),
                                            "duration": matching_place.get("duration", "2h"),
                                            "opening_hours": matching_place.get("opening_hours", "08:00-17:00"),
                                            "rating": float(matching_place.get("rating", 4.0)),
                                            "price": float(matching_place.get("price", 50000)) if matching_place.get("price") else "",
                                            "image_url": image_url,
                                            "url": matching_place.get("url", matching_place.get("link", ""))
                                        }
                                elif required_segment == "evening" and merged_data.get("restaurants"):
                                    rest_index = min(day_num, len(merged_data["restaurants"])-1) if merged_data["restaurants"] else 0
                                    if rest_index >= 0 and merged_data["restaurants"]:
                                        # Get restaurant ID first
                                        restaurant_id = merged_data["restaurants"][rest_index].get("restaurant_id", merged_data["restaurants"][rest_index].get("id", f"restaurant_evening_day{day_num+1}"))
                                        
                                        # Print all restaurant IDs for debugging
                                        log.info(f"Available restaurant IDs: {[r.get('restaurant_id', r.get('id', 'unknown')) for r in merged_data.get('restaurants', [])]}")
                                        log.info(f"Looking for restaurant ID: {restaurant_id}")
                                        
                                        # Find the matching restaurant to get complete data
                                        matching_restaurant = None
                                        for restaurant in merged_data.get("restaurants", []):
                                            # Check for exact matches first
                                            if restaurant.get("restaurant_id") == restaurant_id or restaurant.get("id") == restaurant_id:
                                                matching_restaurant = restaurant
                                                log.info(f"Found exact match for restaurant ID: {restaurant_id}")
                                                break
                                            
                                            # If the restaurant_id contains the ID (e.g., "restaurant_123" contains "123")
                                            elif restaurant_id and restaurant.get("restaurant_id") and restaurant_id in restaurant.get("restaurant_id"):
                                                matching_restaurant = restaurant
                                                log.info(f"Found partial match: {restaurant_id} in {restaurant.get('restaurant_id')}")
                                                break
                                            elif restaurant_id and restaurant.get("id") and restaurant_id in restaurant.get("id"):
                                                matching_restaurant = restaurant
                                                log.info(f"Found partial match: {restaurant_id} in {restaurant.get('id')}")
                                                break
                                        
                                        # If no match found, use the one at rest_index
                                        if not matching_restaurant:
                                            matching_restaurant = merged_data["restaurants"][rest_index]
                                            log.info(f"No match found, using restaurant at index {rest_index}")
                                        
                                        # Log the matched restaurant for debugging
                                        log.info(f"Matched restaurant: {matching_restaurant}")
                                        
                                        # Extract image URL
                                        image_url = ""
                                        if matching_restaurant:
                                            image_url = extract_image_url(matching_restaurant)
                                            log.info(f"Extracted restaurant image URL: {image_url}")
                                        
                                        # Process description - add tour guide style narration
                                        original_description = matching_restaurant.get("description", "")
                                        if original_description:
                                            # Sử dụng nội dung từ original_description nhưng để model tự viết lại
                                            # với giọng văn hướng dẫn viên du lịch
                                            key_points = original_description[:200] if len(original_description) > 200 else original_description
                                            description = f"Hãy cùng thưởng thức bữa ăn tuyệt vời tại nhà hàng đặc biệt này, nơi {key_points.split('.')[0].lower() if '.' in key_points else key_points.lower()}. Bạn sẽ được trải nghiệm những hương vị đặc trưng của ẩm thực địa phương."
                                        else:
                                            description = "Hãy cùng nhau thưởng thức những món ăn đặc sản địa phương tại nhà hàng nổi tiếng này. Bạn sẽ được đắm mình trong hương vị đặc trưng không thể tìm thấy ở nơi nào khác."
                                        
                                        default_activity = {
                                            "id": restaurant_id,
                                            "type": "restaurant",
                                            "name": matching_restaurant.get("name", "Nhà hàng"),
                                            "start_time": "19:00",
                                            "end_time": "21:00",
                                            "description": description,
                                            "address": matching_restaurant.get("address", matching_restaurant.get("location", "")),
                                            "cuisines": matching_restaurant.get("cuisines", "Đặc sản địa phương"),
                                            "price_range": matching_restaurant.get("price_range", "100,000-300,000 VND"),
                                            "rating": float(matching_restaurant.get("rating", 4.2)),
                                            "phone": matching_restaurant.get("phone", ""),
                                            "services": matching_restaurant.get("services", ["đặt bàn"]),
                                            "image_url": image_url,
                                            "url": matching_restaurant.get("url", matching_restaurant.get("link", ""))
                                        }
                            
                            # Only add if we have a valid default activity
                            if default_activity:
                                day_data["segments"].append({
                                    "time_of_day": required_segment,
                                    "activities": [default_activity]
                                })
                            else:
                                # Add empty segment if no default activity can be created
                                day_data["segments"].append({
                                    "time_of_day": required_segment,
                                    "activities": []
                                })
                    
                    # Ensure the first activity of the first day is accommodation
                    if day_num == 0:
                        has_accommodation = False
                        for segment in day_data.get("segments", []):
                            if segment.get("time_of_day") == "morning" and segment.get("activities"):
                                for activity in segment["activities"]:
                                    if activity.get("type") == "accommodation":
                                        has_accommodation = True
                                        log.info(f"Found accommodation in morning activities for day 1")
                                        break
                                if has_accommodation:
                                    break
                        
                        # If no accommodation found in morning segment on day 1, add it
                        if not has_accommodation and merged_data.get("accommodations"):
                            accommodation = merged_data["accommodations"][0]
                            accommodation_id = accommodation.get("accommodation_id", accommodation.get("id", "hotel_day1"))
                            accommodation_name = accommodation.get("name", "Khách sạn")
                            
                            # Create accommodation activity
                            accommodation_activity = {
                                "id": accommodation_id,
                                "type": "accommodation",
                                "name": accommodation_name,
                                "start_time": "08:00",
                                "end_time": "10:00",
                                "description": f"Tại khách sạn tuyệt vời này, bạn sẽ được tận hưởng không gian nghỉ dưỡng thoải mái và tiện nghi. Hãy nghỉ ngơi và chuẩn bị cho những trải nghiệm tuyệt vời tiếp theo!",
                                "location": accommodation.get("location", accommodation.get("address", "")),
                                "booking_link": accommodation.get("booking_link", ""),
                                "room_info": accommodation.get("room_info", "Phòng tiêu chuẩn"),
                                "tax_info": accommodation.get("tax_info", "Đã bao gồm thuế"),
                                "elderly_friendly": accommodation.get("elderly_friendly", True),
                                "rating": float(accommodation.get("rating", 4.5)),
                                "price": float(accommodation.get("price", 850000)),
                                "image_url": accommodation.get("image_url", ""),
                                "url": accommodation.get("url", "")
                            }
                            
                            # Find morning segment or create it
                            morning_segment = None
                            for segment in day_data.get("segments", []):
                                if segment.get("time_of_day") == "morning":
                                    morning_segment = segment
                                    break
                            
                            if morning_segment:
                                # Add to beginning of morning activities
                                morning_segment["activities"].insert(0, accommodation_activity)
                                log.info(f"Added accommodation to existing morning segment for day 1")
                            else:
                                # Create morning segment with accommodation
                                day_data.setdefault("segments", []).insert(0, {
                                    "time_of_day": "morning",
                                    "activities": [accommodation_activity]
                                })
                                log.info(f"Created new morning segment with accommodation for day 1")
                    
                    # Add to the final plan
                    final_plan["plan_by_day"].append(day_data)
                except Exception as e:
                    log.error(f"Error parsing day {day_num+1} data: {e}")
                    # Create a basic day structure
                    basic_day = {
                        "date": current_date_str,
                        "day_title": day_title,
                        "segments": [
                            {"time_of_day": "morning", "activities": []},
                            {"time_of_day": "afternoon", "activities": []},
                            {"time_of_day": "evening", "activities": []}
                        ]
                    }
                    final_plan["plan_by_day"].append(basic_day)
            save_data_to_json(final_plan, f"/Users/doa_ai/Developer/Grab-project/ai/model/src/test_api/generated_plan/plan_{input_data.get('trip_name', 'default_trip')}.json")
            return final_plan
            
        except Exception as e:
            log.error(f"Error in generate_plan: {e}")
            log.debug(f"Input data: {input_data}")
            log.debug(f"Meta data: {meta}")
            
            # Return a basic structure in case of error
            from datetime import datetime
            return {
                "error": str(e),
                "trip_name": input_data.get("trip_name", meta.get("trip_name", "Trip Plan")),
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "end_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                "destination": input_data.get("destination", meta.get("destination", "Unknown")),
                "plan_by_day": []
            }

    

    def _is_primarily_english(self, text):
        """Helper function to determine if text is primarily in English - KHÔNG DÙNG NỮA"""
        # This function is kept for compatibility but no longer used actively
        return False

    def get_trip_plan(merged_data, metadata=None, model_name="gpt-4o", verbose=True):
        """Get a personalized trip plan based on input parameters"""
        start_time = time.time()
        
        try:
            # Initialize chat model
            chat_model = ChatOpenAI(temperature=0.7, model_name=model_name)
            
            # Extract data from merged_data
            destination = merged_data.get("destination", "")
            days = merged_data.get("days", 3)
            start_date = merged_data.get("start_date", "")
            
            if not start_date:
                start_date = datetime.now().strftime("%Y-%m-%d")
            
            # Pass ID maps from metadata to merged_data if available
            if metadata and "accommodation_id_map" in metadata:
                merged_data["accommodation_id_map"] = metadata.get("accommodation_id_map", {})
            if metadata and "place_id_map" in metadata:
                merged_data["place_id_map"] = metadata.get("place_id_map", {})
            if metadata and "restaurant_id_map" in metadata:
                merged_data["restaurant_id_map"] = metadata.get("restaurant_id_map", {})
            
            # Add system message about tour guide style
            system_message = """
            Tạo kế hoạch du lịch chi tiết với giọng văn HƯỚNG DẪN VIÊN DU LỊCH. 
            Mỗi mô tả hoạt động nên sử dụng câu như:
            - "Bạn sẽ được khám phá..."
            - "Hãy cùng thưởng thức..."
            - "Chúng ta sẽ tham quan..."
            - "Quý khách sẽ có cơ hội..."
            
            Mỗi phân đoạn thời gian (sáng, chiều, tối) nên có 2-3 hoạt động liên quan và hợp lý.
            Sử dụng dữ liệu mô tả từ input nhưng PHẢI định dạng lại với giọng văn hướng dẫn viên du lịch.
            """
            
            # Create a complete trip plan
            plan_output = get_complete_trip_plan(merged_data, days, start_date, chat_model, verbose, system_message=system_message)
            
            # Add metadata if provided
            if metadata:
                for key, value in metadata.items():
                    if key not in plan_output.get("plan", {}):
                        plan_output["plan"][key] = value
            
            end_time = time.time()
            if verbose:
                print(f"Trip plan generation completed in {end_time - start_time:.2f} seconds")
            
            return plan_output
            
        except Exception as e:
            print(f"Error generating trip plan: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "plan": {}
            }

    # Thêm hàm giúp xác định thời gian bắt đầu dựa vào thời điểm hiện tại
    def _get_appropriate_start_times(self, current_hour=None):
        """Xác định thời gian bắt đầu phù hợp dựa vào thời điểm hiện tại"""
        from datetime import datetime
        
        if current_hour is None:
            current_hour = datetime.now().hour
        
        # Định nghĩa khung giờ cho các segment
        morning_hours = range(5, 12)   # 5:00 - 11:59
        afternoon_hours = range(12, 18) # 12:00 - 17:59
        evening_hours = range(18, 23)  # 18:00 - 22:59
        
        # Xác định segment hiện tại và các segment còn lại
        current_segment = None
        if current_hour in morning_hours:
            current_segment = "morning"
        elif current_hour in afternoon_hours:
            current_segment = "afternoon"
        elif current_hour in evening_hours:
            current_segment = "evening"
        else:  # Qua nửa đêm (23:00-4:59), chúng ta sẽ lên kế hoạch cho ngày tiếp theo
            current_segment = "next_day"
        
        # Cấu trúc thời gian bắt đầu/kết thúc mặc định cho từng segment
        segment_times = {
            "morning": [
                {"start_time": "08:00", "end_time": "09:30"},
                {"start_time": "10:00", "end_time": "11:30"}
            ],
            "afternoon": [
                {"start_time": "13:00", "end_time": "14:30"},
                {"start_time": "15:00", "end_time": "16:30"}
            ],
            "evening": [
                {"start_time": "18:00", "end_time": "19:30"},
                {"start_time": "20:00", "end_time": "21:30"}
            ]
        }
        
        # Điều chỉnh thời gian bắt đầu dựa vào thời điểm hiện tại
        adjusted_times = {}
        
        if current_segment == "morning":
            # Nếu đang là buổi sáng, điều chỉnh thời gian bắt đầu cho buổi sáng
            start_hour = max(8, current_hour + 1)  # Bắt đầu ít nhất 1 giờ sau giờ hiện tại, không sớm hơn 8:00
            adjusted_times["morning"] = [
                {"start_time": f"{start_hour:02d}:00", "end_time": f"{start_hour+1:02d}:30"},
                {"start_time": f"{start_hour+2:02d}:00", "end_time": f"{start_hour+3:02d}:00"}
            ]
            # Giữ nguyên thời gian cho các segment khác
            adjusted_times["afternoon"] = segment_times["afternoon"]
            adjusted_times["evening"] = segment_times["evening"]
            
        elif current_segment == "afternoon":
            # Bỏ qua buổi sáng, chỉ lên kế hoạch cho buổi chiều và tối
            start_hour = max(13, current_hour + 1)  # Bắt đầu ít nhất 1 giờ sau giờ hiện tại
            adjusted_times["afternoon"] = [
                {"start_time": f"{start_hour:02d}:00", "end_time": f"{start_hour+1:02d}:30"},
                {"start_time": f"{start_hour+2:02d}:00", "end_time": f"{start_hour+3:02d}:00"}
            ]
            adjusted_times["evening"] = segment_times["evening"]
            adjusted_times["morning"] = None  # Đánh dấu buổi sáng không có kế hoạch
            
        elif current_segment == "evening":
            # Bỏ qua buổi sáng và chiều, chỉ lên kế hoạch cho buổi tối
            start_hour = max(18, current_hour + 1)  # Bắt đầu ít nhất 1 giờ sau giờ hiện tại
            adjusted_times["evening"] = [
                {"start_time": f"{start_hour:02d}:00", "end_time": f"{start_hour+1:02d}:30"},
                {"start_time": f"{start_hour+2:02d}:00", "end_time": f"{min(start_hour+3, 23):02d}:00"}
            ]
            adjusted_times["morning"] = None  # Đánh dấu buổi sáng không có kế hoạch
            adjusted_times["afternoon"] = None  # Đánh dấu buổi chiều không có kế hoạch
            
        else:  # next_day - qua nửa đêm, lên kế hoạch cho ngày mai
            # Giữ nguyên tất cả thời gian mặc định
            adjusted_times = segment_times
        
        return adjusted_times, current_segment

    # Thêm hàm xử lý cleanup kết quả từ OpenAI trước khi parse JSON
    def _cleanup_llm_response(self, response_text):
        """
        Làm sạch kết quả từ OpenAI API, đảm bảo chỉ trả về JSON hợp lệ.
        """
        import re
        import json
        
        if not response_text:
            return "{}"
        
        # Log the initial 200 characters of the response for debugging
        log.info(f"Raw response (first 200 chars): {response_text[:200]}")
            
        # Specifically handle the common pattern where there's text before the JSON starts
        # This is the most critical fix - finding the first { that begins the actual JSON object
        # and removing all text before it
        first_brace_index = response_text.find('{')
        if first_brace_index > 0:
            response_text = response_text[first_brace_index:]
            log.info(f"Removed leading text, JSON now starts with: {response_text[:50]}")
            
        # Loại bỏ các tiêu đề và giới thiệu không mong muốn
        cleaned_text = re.sub(r'^(System:|User:|Assistant:|Day \d+:|Ngày \d+:)[^\{]*', '', response_text.strip())
        
        # Try to find a complete JSON object (accounting for nested objects)
        # This uses a more robust approach to find the outermost JSON object
        stack = []
        start_idx = -1
        potential_jsons = []
        
        for i, char in enumerate(cleaned_text):
            if char == '{':
                if not stack:  # If this is the first opening brace
                    start_idx = i
                stack.append('{')
            elif char == '}':
                if stack and stack[-1] == '{':
                    stack.pop()
                    if not stack:  # If we've closed all braces
                        potential_jsons.append(cleaned_text[start_idx:i+1])
        
        # Sort by length (longest first) as it's likely to be more complete
        for json_str in sorted(potential_jsons, key=len, reverse=True):
            try:
                # Try to parse the JSON directly
                json_obj = json.loads(json_str)
                log.info(f"Found valid JSON of length {len(json_str)}")
                return json_str
            except json.JSONDecodeError as e:
                # Try to fix common JSON errors
                try:
                    # Fix trailing commas
                    fixed_json = re.sub(r',\s*([}\]])', r'\1', json_str)
                    # Fix missing quotes around keys
                    fixed_json = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', fixed_json)
                    # Try parsing again
                    json_obj = json.loads(fixed_json)
                    log.info(f"Fixed and parsed JSON of length {len(fixed_json)}")
                    return fixed_json
                except Exception:
                    log.warning(f"Failed to fix JSON: {e}")
                    continue
        
        # If we still haven't found valid JSON, try more aggressive extraction
        # First, try to extract JSON from the first { to the last }
        try:
            first_brace = cleaned_text.find('{')
            last_brace = cleaned_text.rfind('}')
            if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
                json_candidate = cleaned_text[first_brace:last_brace+1]
                try:
                    json.loads(json_candidate)
                    log.info("Extracted JSON from first '{' to last '}', length: " + str(len(json_candidate)))
                    return json_candidate
                except json.JSONDecodeError:
                    # Try fixing common issues
                    # Balance braces
                    open_count = json_candidate.count('{')
                    close_count = json_candidate.count('}')
                    if open_count > close_count:
                        json_candidate += '}' * (open_count - close_count)
                    
                    # Fix trailing commas
                    json_candidate = re.sub(r',\s*([}\]])', r'\1', json_candidate)
                    
                    # Try parsing again
                    try:
                        json.loads(json_candidate)
                        log.info(f"Fixed extracted JSON, length: {len(json_candidate)}")
                        return json_candidate
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            log.warning(f"Error during full JSON extraction: {e}")
            
        # If the balanced braces approach failed, try a more aggressive regex approach
        # This looks for the largest JSON-like structure
        match = re.search(r'(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})', cleaned_text)
        if match:
            try:
                json_str = match.group(1)
                # Remove any trailing or leading non-JSON text
                json_str = re.sub(r'[^{}[\],:"0-9a-zA-Z_\-.\s]+', ' ', json_str)
                # Try to parse
                json.loads(json_str)
                log.info(f"Found valid JSON with regex approach, length {len(json_str)}")
                return json_str
            except json.JSONDecodeError:
                try:
                    # More aggressive fixing
                    # Balance braces
                    open_count = json_str.count('{')
                    close_count = json_str.count('}')
                    if open_count > close_count:
                        json_str += '}' * (open_count - close_count)
                    
                    # Fix common issues
                    # Remove trailing commas
                    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
                    # Ensure property names are quoted
                    json_str = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', json_str)
                    
                    # Try parsing again
                    json.loads(json_str)
                    log.info(f"Fixed JSON with aggressive approach, length {len(json_str)}")
                    return json_str
                except Exception as e:
                    log.warning(f"Failed aggressive JSON fixing: {e}")
        
        # Last resort: try to extract any JSON-like structure with a simpler regex
        json_candidates = re.findall(r'(\{[\s\S]*?\})', cleaned_text)
        if json_candidates:
            for candidate in sorted(json_candidates, key=len, reverse=True):
                try:
                    json.loads(candidate)
                    log.info(f"Found smaller valid JSON fragment, length {len(candidate)}")
                    return candidate
                except json.JSONDecodeError:
                    continue
        
        # If we get here, we couldn't extract a valid JSON
        # Try to create a partial JSON structure with the data we have
        try:
            # Look for properties we can extract
            date_match = re.search(r'"date"\s*:\s*"([^"]+)"', cleaned_text)
            title_match = re.search(r'"day_title"\s*:\s*"([^"]+)"', cleaned_text)
            
            if date_match or title_match:
                partial_json = {
                    "date": date_match.group(1) if date_match else "",
                    "day_title": title_match.group(1) if title_match else "",
                    "segments": []
                }
                log.warning(f"Created partial JSON with extracted properties")
                return json.dumps(partial_json)
        except Exception:
            pass
            
        # Nothing worked, return a minimal JSON structure
        log.error(f"Could not extract valid JSON from: {response_text[:200]}...")
        return '{"error": "Failed to parse response", "segments": []}'


# ---------------------------------------------------------------------------
# 🧪 CLI quick test (python travel_planner.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample_input = {
        "accommodations": [{"id": "hotel42", "name": "Sala", "price": 850000}],
        "places": [{"id": "place10", "name": "Bãi biển Mỹ Khê"}],
        "restaurants": [{"id": "fnb12", "name": "Nhà hàng Bé Mặn"}],
    }
    planner = PlanModel()
    plan = planner.generate_plan(sample_input, trip_name="Test", destination="Đà Nẵng")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
