"""travel_planner.py – rebuilt for explicit JSON output
=================================================================
This version drops the earlier Pydantic schema and instead forces the
LLM to return a **single valid JSON object** that exactly matches the
shape FE/BE yêu cầu (trip_name, start_date, … plan_by_day → segments →
activities …).

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
            You are an expert Vietnamese travel planner specialized in creating detailed, engaging travel itineraries.
            Your recommendations should be specific, authentic, and tailored to the provided data.
            Follow these guidelines:
            1. You are an expert Vietnamese travel planner specialized in creating detailed, engaging travel itineraries.
            2. You must choose for the user the hotel first, to make sure that they can have a suitable hotel. If the next activities is far from the chosen hotel, you must choose another hotel.
            3. Create detailed descriptions in Vietnamese (3-4 sentences per item)
            4. Suggest realistic timings based on location proximity
            5. Include both popular attractions and hidden gems
            6. Consider weather, local events, and seasonal factors
            7. Provide practical tips for transportation between locations
            8. Return ONLY a valid JSON object that exactly matches the requested structure
            9. Use available tools when appropriate to enhance your recommendations
            10. IMPORTANT: Make sure to include only complete, valid JSON - do not cut off any fields or values
            """
            
            # Generate each day individually
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
                Hãy tạo 3 segments (morning, afternoon, evening) với các hoạt động phù hợp.
                
                Thông tin chuyến đi:
                Điểm đến: {merged_data.get("destination")}
                Khách sạn: {[(acc.get("name", ""), acc.get("accommodation_id", "")) for acc in merged_data.get("accommodations", [])]}
                Địa điểm quan tâm: {[(place.get("name", ""), place.get("place_id", "")) for place in merged_data.get("places", [])]}
                Nhà hàng: {[(rest.get("name", ""), rest.get("restaurant_id", "")) for rest in merged_data.get("restaurants", [])]}
                
                QUAN TRỌNG: Trả lời dưới dạng đối tượng JSON đầy đủ, có cấu trúc chính xác như sau:
                {{
                    "date": "{current_date_str}",
                    "day_title": "{day_title}",
                    "segments": [
                        {{
                            "time_of_day": "morning",
                            "activities": [
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
                                    "id": "{merged_data.get('places', [{}])[min(1, len(merged_data.get('places', []))-1)].get('place_id', 'place_morning2_day' + str(day_num+1)) if len(merged_data.get('places', [])) > 1 else 'place_morning2_day' + str(day_num+1)}",
                                    "type": "place",
                                    "name": "Tên địa điểm thứ 2",
                                    "start_time": "10:30",
                                    "end_time": "12:00",
                                    "description": "Mô tả ngắn",
                                    "address": "Địa chỉ đầy đủ",
                                    "categories": "sightseeing",
                                    "duration": "1h30m",
                                    "opening_hours": "08:00-17:00",
                                    "rating": 4.5,
                                    "price": 50000,
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
                                    "id": "{merged_data.get('restaurants', [{}])[min(0, len(merged_data.get('restaurants', []))-1)].get('restaurant_id', 'restaurant_afternoon_day' + str(day_num+1)) if merged_data.get('restaurants') else 'restaurant_afternoon_day' + str(day_num+1)}",
                                    "type": "restaurant",
                                    "name": "Nhà hàng trưa",
                                    "start_time": "15:30",
                                    "end_time": "17:00",
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
                                    "id": "{merged_data.get('places', [{}])[min(3, len(merged_data.get('places', []))-1)].get('place_id', 'place_evening_day' + str(day_num+1)) if len(merged_data.get('places', [])) > 3 else 'place_evening_day' + str(day_num+1)}",
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
                                    "id": "{merged_data.get('restaurants', [{}])[min(1, len(merged_data.get('restaurants', []))-1)].get('restaurant_id', 'restaurant_evening_day' + str(day_num+1)) if len(merged_data.get('restaurants', [])) > 1 else merged_data.get('restaurants', [{}])[0].get('restaurant_id', 'restaurant_evening_day' + str(day_num+1)) if merged_data.get('restaurants') else 'restaurant_evening_day' + str(day_num+1)}",
                                    "type": "restaurant",
                                    "name": "Nhà hàng tối",
                                    "start_time": "19:30",
                                    "end_time": "21:30",
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
                - Nếu description có trong dữ liệu đầu vào, HÃY SỬ DỤNG description đó, nếu là tiếng Anh thì dịch sang tiếng Việt
                - Chỉ trả về đối tượng JSON hợp lệ, không viết gì thêm.
                """
                
                # Generate response for this day
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": day_prompt}
                ]
                
                day_response = self.llm.invoke(messages)
                
                try:
                    # Try to parse the day's data, handling any potential errors
                    try:
                        # First attempt to parse directly
                        day_data = self.parser.parse(day_response)
                    except Exception as json_error:
                        # If that fails, attempt to find and extract a JSON object from the response
                        log.warning(f"Initial JSON parsing failed: {json_error}. Attempting to extract JSON.")
                        import re
                        import json
                        
                        # Find JSON-like content (anything between curly braces)
                        json_match = re.search(r'({[\s\S]*})', day_response)
                        if json_match:
                            try:
                                day_data = json.loads(json_match.group(1))
                            except:
                                # If extraction still fails, use a more robust approach
                                try:
                                    # Try to handle truncated JSON
                                    # Find the last complete segment in case of truncation
                                    partial_json = json_match.group(1)
                                    
                                    # Try to fix common truncation issues by closing brackets
                                    # Count open and closed braces to see if we're missing any
                                    open_braces = partial_json.count('{')
                                    closed_braces = partial_json.count('}')
                                    if open_braces > closed_braces:
                                        # Add missing closing braces
                                        partial_json += '}' * (open_braces - closed_braces)
                                    
                                    # Try to parse the fixed JSON
                                    day_data = json.loads(partial_json)
                                except:
                                    # If all repair attempts fail, create basic structure
                                    log.error(f"Could not repair truncated JSON: {partial_json[:100]}...")
                                    raise ValueError("Could not extract valid JSON after repair attempts")
                        else:
                            # Create basic structure using available data from input
                            log.error("No JSON-like content found in response. Creating basic structure.")
                            
                            # Get current date for this day
                            from datetime import datetime, timedelta
                            if 'start_date' in merged_data and merged_data['start_date']:
                                try:
                                    start_date = datetime.strptime(merged_data['start_date'], "%Y-%m-%d")
                                    current_date = start_date + timedelta(days=day_num)
                                    current_date_str = current_date.strftime("%Y-%m-%d")
                                except:
                                    current_date_str = datetime.now().strftime("%Y-%m-%d")
                            else:
                                current_date_str = datetime.now().strftime("%Y-%m-%d")
                                
                            # Create a basic day structure with empty segments
                            day_data = {
                                "date": current_date_str,
                                "day_title": f"Ngày {day_num+1}: Khám phá",
                                "segments": [
                                    {"time_of_day": "morning", "activities": []},
                                    {"time_of_day": "afternoon", "activities": []},
                                    {"time_of_day": "evening", "activities": []}
                                ]
                            }
                    
                    # Ensure the day has all required segments
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
                                    
                                    # If no match found, use the first one
                                    if not matching_accommodation and merged_data.get("accommodations"):
                                        matching_accommodation = merged_data["accommodations"][0]
                                        log.info(f"No match found, using first accommodation")
                                    
                                    # Log the matched accommodation for debugging
                                    log.info(f"Matched accommodation: {matching_accommodation}")
                                    
                                    # Extract image URL
                                    image_url = ""
                                    if matching_accommodation:
                                        image_url = extract_image_url(matching_accommodation)
                                        log.info(f"Extracted accommodation image URL: {image_url}")
                                    
                                    # Process description - convert to Vietnamese if in English or use existing
                                    original_description = matching_accommodation.get("description", "Check-in và nghỉ ngơi tại khách sạn.") if matching_accommodation else "Check-in và nghỉ ngơi tại khách sạn."
                                    description = original_description
                                    # If description is primarily in English, we'll note that for the LLM to translate
                                    if self._is_primarily_english(original_description):
                                        description = f"[TRANSLATE: {original_description}]"
                                    
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
                                        # Get place ID first
                                        place_id = merged_data["places"][place_index].get("place_id", merged_data["places"][place_index].get("id", f"place_afternoon_day{day_num+1}"))
                                        
                                        # Print all place IDs for debugging
                                        log.info(f"Available place IDs: {[p.get('place_id', p.get('id', 'unknown')) for p in merged_data.get('places', [])]}")
                                        log.info(f"Looking for place ID: {place_id}")
                                        
                                        # Find the matching place to get complete data
                                        matching_place = None
                                        for place in merged_data.get("places", []):
                                            # Check for exact matches first
                                            if place.get("place_id") == place_id or place.get("id") == place_id:
                                                matching_place = place
                                                log.info(f"Found exact match for place ID: {place_id}")
                                                break
                                            
                                            # If the place_id contains the ID (e.g., "place_123" contains "123")
                                            elif place_id and place.get("place_id") and place_id in place.get("place_id"):
                                                matching_place = place
                                                log.info(f"Found partial match: {place_id} in {place.get('place_id')}")
                                                break
                                            elif place_id and place.get("id") and place_id in place.get("id"):
                                                matching_place = place
                                                log.info(f"Found partial match: {place_id} in {place.get('id')}")
                                                break
                                        
                                        # If no match found, use the one at place_index
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
                                        
                                        # Process description - convert to Vietnamese if in English or use existing
                                        original_description = matching_place.get("description", "Tham quan địa điểm nổi tiếng.")
                                        description = original_description
                                        # If description is primarily in English, we'll note that for the LLM to translate
                                        if self._is_primarily_english(original_description):
                                            description = f"[TRANSLATE: {original_description}]"
                                        
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
                                        
                                        # Process description - convert to Vietnamese if in English or use existing
                                        original_description = matching_restaurant.get("description", "Thưởng thức ẩm thực địa phương.") if matching_restaurant else "Thưởng thức ẩm thực địa phương."
                                        description = original_description
                                        # If description is primarily in English, we'll note that for the LLM to translate
                                        if self._is_primarily_english(original_description):
                                            description = f"[TRANSLATE: {original_description}]"
                                        
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

    # ------------------------------------------------------------------
    # 🤖  Agent‑based generation (tool‑ready)
    # ------------------------------------------------------------------
    def generate_plan_with_tools(
        self, input_data: Dict[str, Any], **meta: Any
    ) -> Dict[str, Any]:
        """Agent that can call external tools (weather, maps, etc.)."""
        log.info("Generating plan with agent/tools…")
        
        try:
            # Create a merged data dictionary with meta information
            merged_data = {**input_data, **meta}
            
            # Ensure trip_name exists in the data
            if "trip_name" not in merged_data:
                merged_data["trip_name"] = "Trip to " + merged_data.get("destination", "Unknown")
                
            # Calculate number of days based on start and end dates
            try:
                from datetime import datetime, timedelta
                
                # Set default dates if not provided
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
                # Default to 3 days if dates are invalid or not provided
                log.warning(f"Date parsing error: {date_error}. Using default dates.")
                from datetime import datetime, timedelta
                num_days = 3
                start_date = datetime.now()
                end_date = start_date + timedelta(days=num_days-1)
                merged_data['start_date'] = start_date.strftime("%Y-%m-%d")
                merged_data['end_date'] = end_date.strftime("%Y-%m-%d")
                
            # Initialize the agent
            agent = initialize_agent(
                TOOLS, self.llm, agent="zero-shot-react-description", verbose=False
            )
            
            # Initialize the final plan with basic information
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
            You are an expert Vietnamese travel planner specialized in creating detailed, engaging travel itineraries.
            Your recommendations should be specific, authentic, and tailored to the provided data.
            Follow these guidelines:
            1. You are an expert Vietnamese travel planner specialized in creating detailed, engaging travel itineraries.
            2. You must choose for the user the hotel first, to make sure that they can have a suitable hotel. If the next activities is far from the chosen hotel, you must choose another hotel.
            3. Create detailed descriptions in Vietnamese (3-4 sentences per item)
            4. Suggest realistic timings based on location proximity
            5. Include both popular attractions and hidden gems
            6. Consider weather, local events, and seasonal factors
            7. Provide practical tips for transportation between locations
            8. Return ONLY a valid JSON object that exactly matches the requested structure
            9. Use available tools when appropriate to enhance your recommendations
            10. IMPORTANT: Make sure to include only complete, valid JSON - do not cut off any fields or values
            """
            
            # Generate each day individually
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
                Hãy tạo 3 segments (morning, afternoon, evening) với các hoạt động phù hợp.
                
                Thông tin chuyến đi:
                Điểm đến: {merged_data.get("destination")}
                Khách sạn: {[(acc.get("name", ""), acc.get("accommodation_id", "")) for acc in merged_data.get("accommodations", [])]}
                Địa điểm quan tâm: {[(place.get("name", ""), place.get("place_id", "")) for place in merged_data.get("places", [])]}
                Nhà hàng: {[(rest.get("name", ""), rest.get("restaurant_id", "")) for rest in merged_data.get("restaurants", [])]}
                
                Hãy sử dụng công cụ available tools nếu cần để tìm thông tin thêm.
                
                QUAN TRỌNG: Trả lời dưới dạng đối tượng JSON đầy đủ, có cấu trúc chính xác như sau:
                {{
                    "date": "{current_date_str}",
                    "day_title": "{day_title}",
                    "segments": [
                        {{
                            "time_of_day": "morning",
                            "activities": [{{
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
                            }}]
                        }},
                        {{
                            "time_of_day": "afternoon",
                            "activities": [{{
                                "id": "{merged_data.get('places', [{}])[min(1, len(merged_data.get('places', []))-1)].get('place_id', 'place_afternoon_day' + str(day_num+1)) if len(merged_data.get('places', [])) > 1 else merged_data.get('places', [{}])[0].get('place_id', 'place_afternoon_day' + str(day_num+1)) if merged_data.get('places') else 'place_afternoon_day' + str(day_num+1)}",
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
                            }}]
                        }},
                        {{
                            "time_of_day": "evening",
                            "activities": [{{
                                "id": "{merged_data.get('restaurants', [{}])[0].get('restaurant_id', 'restaurant_evening_day' + str(day_num+1)) if merged_data.get('restaurants') else 'restaurant_evening_day' + str(day_num+1)}",
                                "type": "restaurant",
                                "name": "Tên nhà hàng",
                                "start_time": "19:00",
                                "end_time": "21:00",
                                "description": "Mô tả ngắn",
                                "address": "Địa chỉ đầy đủ", 
                                "cuisines": "Hải sản, Đặc sản địa phương",
                                "price_range": "100,000-300,000 VND",
                                "rating": 4.5,
                                "phone": "0123456789",
                                "services": ["đặt bàn", "giao hàng"],
                                "image_url": "",
                                "url": ""
                            }}]
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
                - Nếu description có trong dữ liệu đầu vào, HÃY SỬ DỤNG description đó, nếu là tiếng Anh thì dịch sang tiếng Việt
                - Chỉ trả về đối tượng JSON hợp lệ, không viết gì thêm.
                """
                
                try:
                    # Run the agent for this day
                    raw_day_response = agent.run(f"{system_prompt}\n\n{day_prompt}")
                    
                    # Try to parse the day's data, handling any potential errors
                    try:
                        # First attempt to parse directly
                        day_data = self.parser.parse(raw_day_response)
                    except Exception as json_error:
                        # If that fails, attempt to find and extract a JSON object from the response
                        log.warning(f"Initial JSON parsing failed: {json_error}. Attempting to extract JSON.")
                        import re
                        import json
                        
                        # Find JSON-like content (anything between curly braces)
                        json_match = re.search(r'({[\s\S]*})', raw_day_response)
                        if json_match:
                            try:
                                day_data = json.loads(json_match.group(1))
                            except:
                                # If extraction still fails, use a more robust approach
                                try:
                                    # Try to handle truncated JSON
                                    # Find the last complete segment in case of truncation
                                    partial_json = json_match.group(1)
                                    
                                    # Try to fix common truncation issues by closing brackets
                                    # Count open and closed braces to see if we're missing any
                                    open_braces = partial_json.count('{')
                                    closed_braces = partial_json.count('}')
                                    if open_braces > closed_braces:
                                        # Add missing closing braces
                                        partial_json += '}' * (open_braces - closed_braces)
                                    
                                    # Try to parse the fixed JSON
                                    day_data = json.loads(partial_json)
                                except:
                                    # If all repair attempts fail, create basic structure
                                    log.error(f"Could not repair truncated JSON: {partial_json[:100]}...")
                                    raise ValueError("Could not extract valid JSON after repair attempts")
                        else:
                            # Create basic structure using available data from input
                            log.error("No JSON-like content found in response. Creating basic structure.")
                            
                            # Get current date for this day
                            from datetime import datetime, timedelta
                            if 'start_date' in merged_data and merged_data['start_date']:
                                try:
                                    start_date = datetime.strptime(merged_data['start_date'], "%Y-%m-%d")
                                    current_date = start_date + timedelta(days=day_num)
                                    current_date_str = current_date.strftime("%Y-%m-%d")
                                except:
                                    current_date_str = datetime.now().strftime("%Y-%m-%d")
                            else:
                                current_date_str = datetime.now().strftime("%Y-%m-%d")
                                
                            # Create a basic day structure with empty segments
                            day_data = {
                                "date": current_date_str,
                                "day_title": f"Ngày {day_num+1}: Khám phá",
                                "segments": [
                                    {"time_of_day": "morning", "activities": []},
                                    {"time_of_day": "afternoon", "activities": []},
                                    {"time_of_day": "evening", "activities": []}
                                ]
                            }
                    
                    # Ensure the day has all required segments
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
                                    
                                    # If no match found, use the first one
                                    if not matching_accommodation and merged_data.get("accommodations"):
                                        matching_accommodation = merged_data["accommodations"][0]
                                        log.info(f"No match found, using first accommodation")
                                    
                                    # Log the matched accommodation for debugging
                                    log.info(f"Matched accommodation: {matching_accommodation}")
                                    
                                    # Extract image URL
                                    image_url = ""
                                    if matching_accommodation:
                                        image_url = extract_image_url(matching_accommodation)
                                        log.info(f"Extracted accommodation image URL: {image_url}")
                                    
                                    # Process description - convert to Vietnamese if in English or use existing
                                    original_description = matching_accommodation.get("description", "Check-in và nghỉ ngơi tại khách sạn.") if matching_accommodation else "Check-in và nghỉ ngơi tại khách sạn."
                                    description = original_description
                                    # If description is primarily in English, we'll note that for the LLM to translate
                                    if self._is_primarily_english(original_description):
                                        description = f"[TRANSLATE: {original_description}]"
                                    
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
                                        # Get place ID first
                                        place_id = merged_data["places"][place_index].get("place_id", merged_data["places"][place_index].get("id", f"place_afternoon_day{day_num+1}"))
                                        
                                        # Print all place IDs for debugging
                                        log.info(f"Available place IDs: {[p.get('place_id', p.get('id', 'unknown')) for p in merged_data.get('places', [])]}")
                                        log.info(f"Looking for place ID: {place_id}")
                                        
                                        # Find the matching place to get complete data
                                        matching_place = None
                                        for place in merged_data.get("places", []):
                                            # Check for exact matches first
                                            if place.get("place_id") == place_id or place.get("id") == place_id:
                                                matching_place = place
                                                log.info(f"Found exact match for place ID: {place_id}")
                                                break
                                            
                                            # If the place_id contains the ID (e.g., "place_123" contains "123")
                                            elif place_id and place.get("place_id") and place_id in place.get("place_id"):
                                                matching_place = place
                                                log.info(f"Found partial match: {place_id} in {place.get('place_id')}")
                                                break
                                            elif place_id and place.get("id") and place_id in place.get("id"):
                                                matching_place = place
                                                log.info(f"Found partial match: {place_id} in {place.get('id')}")
                                                break
                                        
                                        # If no match found, use the one at place_index
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
                                        
                                        # Process description - convert to Vietnamese if in English or use existing
                                        original_description = matching_place.get("description", "Tham quan địa điểm nổi tiếng.")
                                        description = original_description
                                        # If description is primarily in English, we'll note that for the LLM to translate
                                        if self._is_primarily_english(original_description):
                                            description = f"[TRANSLATE: {original_description}]"
                                        
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
                                        
                                        # Process description - convert to Vietnamese if in English or use existing
                                        original_description = matching_restaurant.get("description", "Thưởng thức ẩm thực địa phương.") if matching_restaurant else "Thưởng thức ẩm thực địa phương."
                                        description = original_description
                                        # If description is primarily in English, we'll note that for the LLM to translate
                                        if self._is_primarily_english(original_description):
                                            description = f"[TRANSLATE: {original_description}]"
                                        
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
                    
                    # Add to the final plan
                    final_plan["plan_by_day"].append(day_data)
                    
                except Exception as e:
                    log.error(f"Error generating day {day_num+1} with agent: {e}")
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
            
            return final_plan
            
        except Exception as e:
            log.error(f"Error with agent generation: {e}")
            # Return a basic structure in case of error
            from datetime import datetime, timedelta
            return {
                "error": str(e),
                "trip_name": input_data.get("trip_name", meta.get("trip_name", "Trip Plan")),
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "end_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                "destination": input_data.get("destination", meta.get("destination", "Unknown")),
                "plan_by_day": []
            }

    def _is_primarily_english(self, text):
        """Helper function to determine if text is primarily in English"""
        if not text:
            return False
            
        # Simple heuristic: count English letters vs Vietnamese specific characters
        vietnamese_chars = set('áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ')
        vietnamese_chars.update(set('ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ'))
        
        # Count Vietnamese characters
        vn_count = sum(1 for c in text.lower() if c in vietnamese_chars)
        
        # If very few Vietnamese characters, likely English
        return vn_count < len(text) * 0.05  # Less than 5% Vietnamese characters

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
            
            # Create a complete trip plan
            plan_output = get_complete_trip_plan(merged_data, days, start_date, chat_model, verbose)
            
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
