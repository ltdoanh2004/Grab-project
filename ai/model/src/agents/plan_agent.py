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
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..promts.plan_promt import JSON_SCHEMA_EXAMPLE, system_plan_prompt
from ..utils.helper_function import extract_image_url
<<<<<<< HEAD
from ..agents.review_agent import ReviewAgent
=======
from ..agents.review_agent import TravelReviewer
>>>>>>> edfaf9e (add comment agent)
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from utils.utils import save_data_to_json

ROOT = Path(__file__).resolve().parent
print(ROOT)
load_dotenv(ROOT / ".env")

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
log = logging.getLogger("travel_planner")


FORMAT_INSTRUCTIONS = (
    "Respond ONLY with VALID minified JSON (no markdown) that matches "
    "exactly the structure & keys of the following example: "
    f"{json.dumps(JSON_SCHEMA_EXAMPLE, ensure_ascii=False)}"
)

class PlanModel:
    def __init__(self, temperature: float = 0.7):
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPEN_API_KEY"), 
            temperature=temperature,
            model="gpt-4",  
            max_tokens=4000  
        )
        self.parser = JsonOutputParser()  
<<<<<<< HEAD
        self.review_agent = ReviewAgent()
=======
        self.review_agent = TravelReviewer()
>>>>>>> edfaf9e (add comment agent)


    def _build_prompt(self) -> PromptTemplate:
        template = (
            "You are an expert Vietnamese travel planner. Using the user data, "
            "generate a coherent multi‑day trip strictly in JSON format.\n\n"
            "IMPORTANT: Your response MUST be ONLY VALID JSON. "
            "Do NOT include any text before or after the JSON. "
            "Do NOT add title, notes, or explanations.\n\n"
            "User context (JSON): {user_json}\n\n" + FORMAT_INSTRUCTIONS
        )
        return PromptTemplate(template=template, input_variables=["user_json"])

    def _build_day_prompt(self, day_num: int, current_date_str: str, merged_data: Dict[str, Any]) -> str:
        """Build the prompt for generating a specific day's plan.
        
        Args:
            day_num: The day number (0-based)
            current_date_str: The current date in YYYY-MM-DD format
            merged_data: The merged input data containing accommodations, places, restaurants
            
        Returns:
            str: The complete prompt for generating the day's plan
        """
        self.day_title = f"Ngày {day_num+1}: "
        if day_num == 0:
            self.day_title += "Khám phá biển"
        elif day_num == 1:
            self.day_title += "Khám phá núi"
        elif day_num == 2:
            self.day_title += "Khám phá văn hóa"
        else:
            self.day_title += "Khám phá địa phương"
        
        day_prompt = f"""
        Tạo chi tiết cho ngày {day_num+1} (ngày {current_date_str}) của lịch trình du lịch {merged_data.get("destination")}.
        Tạo 3 segments (morning, afternoon, evening) với các hoạt động phù hợp.
        
        CHÚ Ý QUAN TRỌNG: 
        1. CHỈ TRẢ VỀ JSON THUẦN TÚY! KHÔNG THÊM BẤT KỲ VĂN BẢN NÀO TRƯỚC HOẶC SAU JSON!
        2. PHẢN HỒI CỦA BẠN PHẢI BẮT ĐẦU BẰNG DẤU "{{" VÀ KẾT THÚC BẰNG DẤU "}}" - KHÔNG CÓ GÌ KHÁC!
        3. MÔ TẢ PHẢI NGẮN GỌN (<100 ký tự) để tránh vượt quá giới hạn token
        4. KHÔNG sử dụng mô tả dài, CHỈ 1-2 câu ngắn gọn
        5. JSON KHÔNG ĐƯỢC CẮT NGẮN GIỮA CHỪNG - KIỂM TRA KỸ TẤT CẢ DẤU NGOẶC ĐỀU ĐƯỢC ĐÓNG!
        
        Thông tin chuyến đi:
        Điểm đến: {merged_data.get("destination")}
        Khách sạn: {[(acc.get("name", ""), acc.get("accommodation_id", "")) for acc in merged_data.get("accommodations", [])]}
        Địa điểm: {[(place.get("name", ""), place.get("place_id", "")) for place in merged_data.get("places", [])]}
        Nhà hàng: {[(rest.get("name", ""), rest.get("restaurant_id", "")) for rest in merged_data.get("restaurants", [])]}
        
        Cấu trúc JSON cần tuân thủ:
        {{
            "date": "{current_date_str}",
            "day_title": "Ngày {day_num+1}: [Tiêu đề ngắn gọn]",
            "segments": [
                {{
                    "time_of_day": "morning",
                    "activities": [
                        {{
                            "id": "[ID CHÍNH XÁC từ dữ liệu]",
                            "type": "accommodation",
                            "name": "Tên hoạt động",
                            "start_time": "08:00",
                            "end_time": "10:00",
                            "description": "Bạn sẽ được...",
                            // Các trường khác tùy loại hoạt động
                        }}
                    ]
                }},
                // Tương tự cho afternoon và evening
            ]
        }}
        
        Hướng dẫn quan trọng:
        - Tiêu đề ngày PHẢI NGẮN GỌN và sáng tạo (ví dụ: "Khám phá Hà Nội cổ kính")
        - GIẢM ĐỘ DÀI mô tả, chỉ cần 1-2 câu ngắn với phong cách hướng dẫn viên
        - Luôn sử dụng đúng ID từ dữ liệu đầu vào
        - Mỗi segment có 1-2 hoạt động (KHÔNG cần 3 hoạt động/segment để giảm kích thước JSON)
        - XÓA tất cả chú thích, hướng dẫn trong JSON cuối cùng
        - Description phải ngắn gọn sáng tạo và có thể chèn thêm icon. 
        """
        
        day_prompt += f"""
        
        Đây là ví dụ chuẩn về JSON ngắn gọn cần tạo (NHƯNG PHẢI THAY BẰNG DỮ LIỆU THỰC TẾ):
        
        {{
            "date": "{current_date_str}",
            "day_title": "Ngày {day_num+1}: Khám phá Hà Nội",
            "segments": [
                {{
                    "time_of_day": "morning",
                    "activities": [
                        {{
                            "id": "hotel_123",
                            "type": "accommodation",
                            "name": "Khách sạn ABC",
                            "start_time": "08:00", 
                            "end_time": "10:00",
                            "description": "Bạn sẽ được tận hưởng không gian nghỉ dưỡng thoải mái.",
                            "location": "Hà Nội",
                            "rating": 4.5,
                            "price": 850000,
                            "image_url": "",
                            "url": ""
                        }}
                    ]
                }},
                {{
                    "time_of_day": "afternoon",
                    "activities": [
                        {{
                            "id": "place_456",
                            "type": "place",
                            "name": "Địa điểm XYZ",
                            "start_time": "13:00",
                            "end_time": "15:00",
                            "description": "Hãy khám phá nét văn hóa đặc sắc tại địa điểm này.",
                            "address": "Hà Nội",
                            "categories": "sightseeing",
                            "rating": 4.5,
                            "price": 50000,
                            "image_url": "",
                            "url": ""
                        }}
                    ]
                }},
                {{
                    "time_of_day": "evening",
                    "activities": [
                        {{
                            "id": "restaurant_789",
                            "type": "restaurant",
                            "name": "Nhà hàng XYZ",
                            "start_time": "18:00",
                            "end_time": "20:00",
                            "description": "Thưởng thức ẩm thực đặc sắc tại nhà hàng nổi tiếng.",
                            "address": "Hà Nội",
                            "cuisines": "Đặc sản địa phương",
                            "rating": 4.5,
                            "phone": "",
                            "image_url": "",
                            "url": ""
                        }}
                    ]
                }}
            ]
        }}
        
        NHẮC LẠI: JSON phải ngắn gọn và hoàn chỉnh, không được có chú thích hay bị thiếu dấu ngoặc.
        """
        
        return day_prompt

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
            
            system_prompt = system_plan_prompt
            
            for day_num in range(num_days):
                current_date = start_date + timedelta(days=day_num)
                current_date_str = current_date.strftime("%Y-%m-%d")
                
                day_prompt = self._build_day_prompt(day_num, current_date_str, merged_data)
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": day_prompt}
                ]
                
                try:
                    day_response = self.llm.invoke(messages)
                    
                    day_response_content = day_response.content if hasattr(day_response, 'content') else day_response
                    
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
                        
                        for required_segment in ["morning", "afternoon", "evening"]:
                            if required_segment not in existing_segments:
                                

                                if required_segment not in existing_segments:
                                    default_activity = {}
                                    if required_segment == "morning" and merged_data.get("accommodations"):
                                        accommodation_id = merged_data["accommodations"][0].get("accommodation_id", merged_data["accommodations"][0].get("id", f"hotel_morning_day{day_num+1}"))
                                        
                                        log.info(f"Available accommodation IDs: {[a.get('accommodation_id', a.get('id', 'unknown')) for a in merged_data.get('accommodations', [])]}")
                                        log.info(f"Looking for accommodation ID: {accommodation_id}")
                                        
                                        matching_accommodation = None
                                        for acc in merged_data.get("accommodations", []):
                                            if acc.get("accommodation_id") == accommodation_id or acc.get("id") == accommodation_id:
                                                matching_accommodation = acc
                                                log.info(f"Found exact match for accommodation ID: {accommodation_id}")
                                                break
                                            
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
                                            restaurant_id = merged_data["restaurants"][rest_index].get("restaurant_id", merged_data["restaurants"][rest_index].get("id", f"restaurant_evening_day{day_num+1}"))
                                            
                                            log.info(f"Available restaurant IDs: {[r.get('restaurant_id', r.get('id', 'unknown')) for r in merged_data.get('restaurants', [])]}")
                                            log.info(f"Looking for restaurant ID: {restaurant_id}")
                                            
                                            matching_restaurant = None
                                            for restaurant in merged_data.get("restaurants", []):
                                                if restaurant.get("restaurant_id") == restaurant_id or restaurant.get("id") == restaurant_id:
                                                    matching_restaurant = restaurant
                                                    log.info(f"Found exact match for restaurant ID: {restaurant_id}")
                                                    break
                                                
                                                elif restaurant_id and restaurant.get("restaurant_id") and restaurant_id in restaurant.get("restaurant_id"):
                                                    matching_restaurant = restaurant
                                                    log.info(f"Found partial match: {restaurant_id} in {restaurant.get('restaurant_id')}")
                                                    break
                                                elif restaurant_id and restaurant.get("id") and restaurant_id in restaurant.get("id"):
                                                    matching_restaurant = restaurant
                                                    log.info(f"Found partial match: {restaurant_id} in {restaurant.get('id')}")
                                                    break
                                            
                                            if not matching_restaurant:
                                                matching_restaurant = merged_data["restaurants"][rest_index]
                                                log.info(f"No match found, using restaurant at index {rest_index}")
                                            
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
                            "day_title": self.day_title,
                            "segments": [
                                {"time_of_day": "morning", "activities": []},
                                {"time_of_day": "afternoon", "activities": []},
                                {"time_of_day": "evening", "activities": []}
                            ]
                        }   
                        # Bổ sung các hoạt động mặc định cho ngày này
                        basic_day = self._populate_default_activities(basic_day, day_num, merged_data)
                        final_plan["plan_by_day"].append(basic_day)
                except Exception as e:
                    log.error(f"Error parsing day {day_num+1} data: {e}")
                    # Create a basic day structure
                    basic_day = {
                        "date": current_date_str,
                        "day_title": self.day_title,
                        "segments": [
                            {"time_of_day": "morning", "activities": []},
                            {"time_of_day": "afternoon", "activities": []},
                            {"time_of_day": "evening", "activities": []}
                        ]
                    }
                    basic_day = self._populate_default_activities(basic_day, day_num, merged_data)
                    final_plan["plan_by_day"].append(basic_day)
            
            for idx, day in enumerate(final_plan["plan_by_day"]):
                empty_segments = []
                for segment in day.get("segments", []):
                    if not segment.get("activities"):
                        empty_segments.append(segment["time_of_day"])
            
                if empty_segments:
                    log.info(f"Ngày {idx+1} có {len(empty_segments)} segment trống, đang bổ sung hoạt động mặc định")
                    day = self._populate_default_activities(day, idx, merged_data)
            
            save_data_to_json(final_plan, f"/Users/doa_ai/Developer/Grab-project/ai/model/src/test_api/generated_plan/plan_{input_data.get('trip_name', 'default_trip')}.json")
            review_plan = self.review_agent.process_plan(final_plan)
            return review_plan
            
        except Exception as e:
            log.error(f"Error in generate_plan: {e}")
            log.debug(f"Input data: {input_data}")
            log.debug(f"Meta data: {meta}")
            

            return {
                "error": str(e),
                "trip_name": input_data.get("trip_name", meta.get("trip_name", "Trip Plan")),
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "end_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                "destination": input_data.get("destination", meta.get("destination", "Unknown")),
                "plan_by_day": []
            }

    def _get_appropriate_start_times(self, current_hour=None):
        """Xác định thời gian bắt đầu phù hợp dựa vào thời điểm hiện tại"""
        from datetime import datetime
        
        if current_hour is None:
            current_hour = datetime.now().hour
        
        morning_hours = range(5, 12)   # 5:00 - 11:59
        afternoon_hours = range(12, 18) # 12:00 - 17:59
        evening_hours = range(18, 23)  # 18:00 - 22:59
        
        current_segment = None
        if current_hour in morning_hours:
            current_segment = "morning"
        elif current_hour in afternoon_hours:
            current_segment = "afternoon"
        elif current_hour in evening_hours:
            current_segment = "evening"
        else:  
            current_segment = "next_day"
        
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
        
        adjusted_times = {}
        if current_segment == "morning":
            start_hour = max(8, current_hour + 1)  
            adjusted_times["morning"] = [
                {"start_time": f"{start_hour:02d}:00", "end_time": f"{start_hour+1:02d}:30"},
                {"start_time": f"{start_hour+2:02d}:00", "end_time": f"{start_hour+3:02d}:00"}
            ]
            adjusted_times["afternoon"] = segment_times["afternoon"]
            adjusted_times["evening"] = segment_times["evening"]
            
        elif current_segment == "afternoon":
            start_hour = max(13, current_hour + 1) 
            adjusted_times["afternoon"] = [
                {"start_time": f"{start_hour:02d}:00", "end_time": f"{start_hour+1:02d}:30"},
                {"start_time": f"{start_hour+2:02d}:00", "end_time": f"{start_hour+3:02d}:00"}
            ]
            adjusted_times["evening"] = segment_times["evening"]
            adjusted_times["morning"] = None  
            
        elif current_segment == "evening":
            start_hour = max(18, current_hour + 1) 
            adjusted_times["evening"] = [
                {"start_time": f"{start_hour:02d}:00", "end_time": f"{start_hour+1:02d}:30"},
                {"start_time": f"{start_hour+2:02d}:00", "end_time": f"{min(start_hour+3, 23):02d}:00"}
            ]
            adjusted_times["morning"] = None  
            adjusted_times["afternoon"] = None  
            
        else:  
            adjusted_times = segment_times
        
        return adjusted_times, current_segment

    def _cleanup_llm_response(self, response_text):
        """
        Làm sạch kết quả từ OpenAI API, đảm bảo chỉ trả về JSON hợp lệ.
        """
        import re
        import json
        
        if not response_text:
            return "{}"
        
        log.info(f"Raw response (first 200 chars): {response_text[:200]}")
            

        first_brace_index = response_text.find('{')
        if first_brace_index > 0:
            response_text = response_text[first_brace_index:]
            log.info(f"Removed leading text, JSON now starts with: {response_text[:50]}")
            
        cleaned_text = re.sub(r'^(System:|User:|Assistant:|Day \d+:|Ngày \d+:)[^\{]*', '', response_text.strip())
        

        stack = []
        start_idx = -1
        potential_jsons = []
        
        for i, char in enumerate(cleaned_text):
            if char == '{':
                if not stack:  
                    start_idx = i
                stack.append('{')
            elif char == '}':
                if stack and stack[-1] == '{':
                    stack.pop()
                    if not stack:  
                        potential_jsons.append(cleaned_text[start_idx:i+1])
        
        for json_str in sorted(potential_jsons, key=len, reverse=True):
            try:
                json_obj = json.loads(json_str)
                log.info(f"Found valid JSON of length {len(json_str)}")
                return json_str
            except json.JSONDecodeError as e:
                try:
                    fixed_json = re.sub(r',\s*([}\]])', r'\1', json_str)
                    fixed_json = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', fixed_json)
                    
                    fixed_json = re.sub(r'//.*?\n', '', fixed_json)
                    fixed_json = re.sub(r'/\*.*?\*/', '', fixed_json, flags=re.DOTALL)
                    
                    json_obj = json.loads(fixed_json)
                    log.info(f"Fixed and parsed JSON of length {len(fixed_json)}")
                    return fixed_json
                except Exception:
                    log.warning(f"Failed to fix JSON: {e}")
                    continue
        

        try:
            json_fragment = cleaned_text
            if cleaned_text.find("{") != -1:
                json_fragment = cleaned_text[cleaned_text.find("{"):]
            
            date_match = re.search(r'"date"\s*:\s*"([^"]+)"', json_fragment)
            title_match = re.search(r'"day_title"\s*:\s*"([^"]+)"', json_fragment)
            
            if date_match or title_match:
                partial_json = {
                    "date": date_match.group(1) if date_match else "",
                    "day_title": title_match.group(1) if title_match else "",
                    "segments": []
                }
                
                morning_match = re.search(r'"time_of_day"\s*:\s*"morning"', json_fragment)
                if morning_match:
                    morning_activities = []
                    hotel_match = re.search(r'"type"\s*:\s*"accommodation"[\s\S]*?(?=},|}\])', json_fragment)
                    if hotel_match:
                        try:
                            hotel_id_match = re.search(r'"id"\s*:\s*"([^"]+)"', hotel_match.group(0))
                            hotel_name_match = re.search(r'"name"\s*:\s*"([^"]+)"', hotel_match.group(0))
                            hotel_desc_match = re.search(r'"description"\s*:\s*"([^"]+)"', hotel_match.group(0))
                            
                            if hotel_id_match:
                                hotel_activity = {
                                    "id": hotel_id_match.group(1),
                                    "type": "accommodation",
                                    "name": hotel_name_match.group(1) if hotel_name_match else "Khách sạn",
                                    "start_time": "08:00",
                                    "end_time": "10:00",
                                    "description": hotel_desc_match.group(1) if hotel_desc_match else "Bạn sẽ được tận hưởng không gian nghỉ ngơi tại khách sạn này.",
                                    "location": "",
                                    "rating": 4.5,
                                    "price": 850000,
                                    "image_url": "",
                                    "url": ""
                                }
                                morning_activities.append(hotel_activity)
                        except Exception as e:
                            log.warning(f"Error extracting hotel info: {e}")
                    
                    if morning_activities:
                        partial_json["segments"].append({
                            "time_of_day": "morning",
                            "activities": morning_activities
                        })
                
                afternoon_match = re.search(r'"time_of_day"\s*:\s*"afternoon"', json_fragment)
                if afternoon_match:
                    partial_json["segments"].append({
                        "time_of_day": "afternoon",
                        "activities": []
                    })
                
                evening_match = re.search(r'"time_of_day"\s*:\s*"evening"', json_fragment)
                if evening_match:
                    partial_json["segments"].append({
                        "time_of_day": "evening",
                        "activities": []
                    })
                
                if not partial_json["segments"]:
                    partial_json["segments"] = [
                        {"time_of_day": "morning", "activities": []},
                        {"time_of_day": "afternoon", "activities": []},
                        {"time_of_day": "evening", "activities": []}
                    ]
                
                log.warning(f"Created partial JSON with extracted properties from truncated response")
                return json.dumps(partial_json)
        except Exception as e:
            log.error(f"Error during partial extraction: {e}")
            

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
                    open_count = json_candidate.count('{')
                    close_count = json_candidate.count('}')
                    if open_count > close_count:
                        json_candidate += '}' * (open_count - close_count)
                    
                    json_candidate = re.sub(r',\s*([}\]])', r'\1', json_candidate)
                    
                    try:
                        json.loads(json_candidate)
                        log.info(f"Fixed extracted JSON, length: {len(json_candidate)}")
                        return json_candidate
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            log.warning(f"Error during full JSON extraction: {e}")
            
        match = re.search(r'(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})', cleaned_text)
        if match:
            try:
                json_str = match.group(1)
                json_str = re.sub(r'[^{}[\],:"0-9a-zA-Z_\-.\s]+', ' ', json_str)
                json.loads(json_str)
                log.info(f"Found valid JSON with regex approach, length {len(json_str)}")
                return json_str
            except json.JSONDecodeError:
                try:
                    open_count = json_str.count('{')
                    close_count = json_str.count('}')
                    if open_count > close_count:
                        json_str += '}' * (open_count - close_count)
                    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
                    json_str = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', json_str)
                    
                    json.loads(json_str)
                    log.info(f"Fixed JSON with aggressive approach, length {len(json_str)}")
                    return json_str
                except Exception as e:
                    log.warning(f"Failed aggressive JSON fixing: {e}")
        
        json_candidates = re.findall(r'(\{[\s\S]*?\})', cleaned_text)
        if json_candidates:
            for candidate in sorted(json_candidates, key=len, reverse=True):
                try:
                    json.loads(candidate)
                    log.info(f"Found smaller valid JSON fragment, length {len(candidate)}")
                    return candidate
                except json.JSONDecodeError:
                    continue
        
        try:
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
            
        log.error(f"Could not extract valid JSON from: {response_text[:200]}...")
        return '{"error": "Failed to parse response", "segments": []}'

    def _populate_default_activities(self, day_data, day_num, merged_data):
        """Đảm bảo mỗi segment đều có ít nhất một hoạt động mặc định"""
        
        existing_segments = {segment.get("time_of_day"): segment for segment in day_data.get("segments", [])}
        
        
        for segment_type in ["morning", "afternoon", "evening"]:
            segment = existing_segments.get(segment_type)
            
            if not segment:
                segment = {"time_of_day": segment_type, "activities": []}
                day_data["segments"].append(segment)
                existing_segments[segment_type] = segment
            
            if not segment.get("activities"):
                activities = []
                
                if segment_type == "morning" and merged_data.get("accommodations"):
                    accommodation = merged_data["accommodations"][0]
                    accommodation_id = accommodation.get("accommodation_id", accommodation.get("id", f"hotel_morning_day{day_num+1}"))
                    
                    matching_accommodation = None
                    for acc in merged_data.get("accommodations", []):
                        if (acc.get("accommodation_id") == accommodation_id or 
                            acc.get("id") == accommodation_id):
                            matching_accommodation = acc
                            break
                    
                    if not matching_accommodation and merged_data.get("accommodations"):
                        matching_accommodation = merged_data["accommodations"][0]
                    
                    image_url = ""
                    if matching_accommodation:
                        image_url = extract_image_url(matching_accommodation)
                    
                    description = "Bạn sẽ được tận hưởng không gian thoải mái tại khách sạn này. Đây là nơi lý tưởng để nghỉ ngơi và chuẩn bị cho hành trình khám phá thú vị phía trước."
                    
                    activities.append({
                        "id": accommodation_id,
                        "type": "accommodation",
                        "name": matching_accommodation.get("name", "Khách sạn") if matching_accommodation else "Khách sạn",
                        "start_time": "08:00",
                        "end_time": "10:00",
                        "description": description,
                        "location": matching_accommodation.get("location", matching_accommodation.get("address", "")) if matching_accommodation else "",
                        "rating": float(matching_accommodation.get("rating", 4.5)) if matching_accommodation else 4.5,
                        "price": float(matching_accommodation.get("price", 850000)) if matching_accommodation else 850000,
                        "image_url": image_url,
                        "booking_link": matching_accommodation.get("booking_link", "") if matching_accommodation else "",
                        "room_info": matching_accommodation.get("room_info", "Phòng tiêu chuẩn") if matching_accommodation else "Phòng tiêu chuẩn",
                        "tax_info": matching_accommodation.get("tax_info", "Đã bao gồm thuế") if matching_accommodation else "Đã bao gồm thuế",
                        "elderly_friendly": matching_accommodation.get("elderly_friendly", True) if matching_accommodation else True,
                        "url": matching_accommodation.get("url", matching_accommodation.get("link", "")) if matching_accommodation else ""
                    })
                
                elif segment_type == "afternoon" and merged_data.get("places"):
                    place_index = min(day_num, len(merged_data["places"])-1) if merged_data["places"] else 0
                    if place_index >= 0 and merged_data["places"]:
                        place = merged_data["places"][place_index]
                        place_id = place.get("place_id", place.get("id", f"place_afternoon_day{day_num+1}"))
                        
                        image_url = extract_image_url(place)
                        
                        description = "Bạn sẽ được khám phá địa điểm tuyệt vời này với những cảnh quan độc đáo. Hãy chuẩn bị máy ảnh để lưu lại những khoảnh khắc đáng nhớ!"
                        
                        activities.append({
                            "id": place_id,
                            "type": "place",
                            "name": place.get("name", "Địa điểm tham quan"),
                            "start_time": "14:00",
                            "end_time": "16:00",
                            "description": description,
                            "address": place.get("address", place.get("location", "")),
                            "categories": place.get("categories", "sightseeing"),
                            "duration": place.get("duration", "2h"),
                            "opening_hours": place.get("opening_hours", "08:00-17:00"),
                            "rating": float(place.get("rating", 4.5)),
                            "price": float(place.get("price", 50000)) if place.get("price") else 0,
                            "image_url": image_url,
                            "url": place.get("url", place.get("link", ""))
                        })
                
                elif segment_type == "evening" and merged_data.get("restaurants"):
                    rest_index = min(day_num, len(merged_data["restaurants"])-1) if merged_data["restaurants"] else 0
                    if rest_index >= 0 and merged_data["restaurants"]:
                        restaurant = merged_data["restaurants"][rest_index]
                        restaurant_id = restaurant.get("restaurant_id", restaurant.get("id", f"restaurant_evening_day{day_num+1}"))
                        
                        image_url = extract_image_url(restaurant)
                        
                        description = "Hãy cùng thưởng thức những món ăn đặc sản địa phương tại nhà hàng này. Bạn sẽ được đắm mình trong hương vị đặc trưng không thể tìm thấy ở nơi nào khác."
                        
                        activities.append({
                            "id": restaurant_id,
                            "type": "restaurant",
                            "name": restaurant.get("name", "Nhà hàng"),
                            "start_time": "19:00",
                            "end_time": "21:00",
                            "description": description,
                            "address": restaurant.get("address", restaurant.get("location", "")),
                            "cuisines": restaurant.get("cuisines", "Đặc sản địa phương"),
                            "price_range": restaurant.get("price_range", "100,000-300,000 VND"),
                            "rating": float(restaurant.get("rating", 4.5)),
                            "phone": restaurant.get("phone", ""),
                            "services": restaurant.get("services", ["đặt bàn"]),
                            "image_url": image_url,
                            "url": restaurant.get("url", restaurant.get("link", ""))
                        })
                
                if activities:
                    segment["activities"] = activities
        
        sorted_segments = []
        for segment_type in ["morning", "afternoon", "evening"]:
            if segment_type in existing_segments:
                sorted_segments.append(existing_segments[segment_type])
        
        day_data["segments"] = sorted_segments
        return day_data


if __name__ == "__main__":
    sample_input = {
        "accommodations": [{"id": "hotel42", "name": "Sala", "price": 850000}],
        "places": [{"id": "place10", "name": "Bãi biển Mỹ Khê"}],
        "restaurants": [{"id": "fnb12", "name": "Nhà hàng Bé Mặn"}],
    }
    planner = PlanModel()
    plan = planner.generate_plan(sample_input, trip_name="Test", destination="Đà Nẵng")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
