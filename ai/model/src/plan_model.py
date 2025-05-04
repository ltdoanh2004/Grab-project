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

from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI

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
        # Use OPEN_API_KEY since that's what's set in the environment
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
            1. Create detailed descriptions in Vietnamese (3-4 sentences per item)
            2. Suggest realistic timings based on location proximity
            3. Include both popular attractions and hidden gems
            4. Consider weather, local events, and seasonal factors
            5. Provide practical tips for transportation between locations
            6. Return ONLY a valid JSON object that exactly matches the requested structure
            7. IMPORTANT: Make sure to include only complete, valid JSON - do not cut off any fields or values
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
                Khách sạn: {[acc.get("name", "") for acc in merged_data.get("accommodations", [])]}
                Địa điểm quan tâm: {[place.get("name", "") for place in merged_data.get("places", [])]}
                Nhà hàng: {[rest.get("name", "") for rest in merged_data.get("restaurants", [])]}
                
                QUAN TRỌNG: Trả lời dưới dạng đối tượng JSON đầy đủ, có cấu trúc chính xác như sau:
                {{
                    "date": "{current_date_str}",
                    "day_title": "{day_title}",
                    "segments": [
                        {{
                            "time_of_day": "morning",
                            "activities": [{{
                                "id": "place_morning_day{day_num+1}",
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
                                "id": "place_afternoon_day{day_num+1}",
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
                                "id": "restaurant_evening_day{day_num+1}",
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
                
                2. Nếu type là "place":
                   - Bổ sung: "categories", "duration", "opening_hours"
                   - Giữ nguyên "address"
                   - Price là số nguyên nếu có (VND)
                
                3. Nếu type là "restaurant":
                   - Bổ sung: "cuisines", "price_range", "phone", "services" (array)
                   - Giữ nguyên "address"
                
                QUAN TRỌNG: Chỉ trả về đối tượng JSON hợp lệ, không viết gì thêm.
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
                                # If extraction still fails, create a basic structure
                                raise ValueError("Could not extract valid JSON")
                        else:
                            raise ValueError("No JSON-like content found in response")
                    
                    # Ensure the day has all required segments
                    if "segments" not in day_data or not day_data["segments"]:
                        day_data["segments"] = []
                    
                    existing_segments = {segment.get("time_of_day"): segment for segment in day_data["segments"]}
                    
                    # Check for required segments and add if missing
                    for required_segment in ["morning", "afternoon", "evening"]:
                        if required_segment not in existing_segments:
                            # Create a basic segment with default activity
                            default_activity = {}
                            if required_segment == "morning" and merged_data.get("accommodations"):
                                default_activity = {
                                    "id": merged_data["accommodations"][0].get("accommodation_id", f"hotel_morning_day{day_num+1}"),
                                    "type": "accommodation",
                                    "name": merged_data["accommodations"][0].get("name", "Khách sạn"),
                                    "start_time": "08:00",
                                    "end_time": "10:00",
                                    "description": "Check-in và nghỉ ngơi tại khách sạn.",
                                    "location": merged_data["accommodations"][0].get("location", ""),
                                    "rating": float(merged_data["accommodations"][0].get("rating", 4.5)),
                                    "price": float(merged_data["accommodations"][0].get("price", 850000)),
                                    "image_url": merged_data["accommodations"][0].get("image_url", ""),
                                    "booking_link": merged_data["accommodations"][0].get("booking_link", ""),
                                    "room_info": merged_data["accommodations"][0].get("room_info", "Phòng tiêu chuẩn, 2 giường"),
                                    "tax_info": merged_data["accommodations"][0].get("tax_info", "Đã bao gồm thuế VAT"),
                                    "elderly_friendly": merged_data["accommodations"][0].get("elderly_friendly", True),
                                    "url": merged_data["accommodations"][0].get("url", "")
                                }
                            elif required_segment == "afternoon" and merged_data.get("places"):
                                place_index = min(day_num, len(merged_data["places"])-1) if merged_data["places"] else 0
                                if place_index >= 0 and merged_data["places"]:
                                    place = merged_data["places"][place_index]
                                    default_activity = {
                                        "id": place.get("place_id", f"place_afternoon_day{day_num+1}"),
                                        "type": "place",
                                        "name": place.get("name", "Địa điểm tham quan"),
                                        "start_time": "14:00",
                                        "end_time": "16:00",
                                        "description": place.get("description", "Tham quan địa điểm nổi tiếng."),
                                        "address": place.get("address", ""),
                                        "categories": place.get("categories", "sightseeing"),
                                        "duration": place.get("duration", "2h"),
                                        "opening_hours": place.get("opening_hours", "08:00-17:00"),
                                        "rating": float(place.get("rating", 4.0)),
                                        "price": float(place.get("price", 50000)) if place.get("price") else "",
                                        "image_url": place.get("image_url", ""),
                                        "url": place.get("url", "")
                                    }
                            elif required_segment == "evening" and merged_data.get("restaurants"):
                                rest_index = min(day_num, len(merged_data["restaurants"])-1) if merged_data["restaurants"] else 0
                                if rest_index >= 0 and merged_data["restaurants"]:
                                    restaurant = merged_data["restaurants"][rest_index]
                                    default_activity = {
                                        "id": restaurant.get("restaurant_id", f"restaurant_evening_day{day_num+1}"),
                                        "type": "restaurant",
                                        "name": restaurant.get("name", "Nhà hàng"),
                                        "start_time": "19:00",
                                        "end_time": "21:00",
                                        "description": restaurant.get("description", "Thưởng thức ẩm thực địa phương."),
                                        "address": restaurant.get("address", ""),
                                        "cuisines": restaurant.get("cuisines", "Đặc sản địa phương"),
                                        "price_range": restaurant.get("price_range", "100,000-300,000 VND"),
                                        "rating": float(restaurant.get("rating", 4.2)),
                                        "phone": restaurant.get("phone", ""),
                                        "services": restaurant.get("services", ["đặt bàn"]),
                                        "image_url": restaurant.get("image_url", ""),
                                        "url": restaurant.get("url", "")
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
            1. Create detailed descriptions in Vietnamese (3-4 sentences per item)
            2. Suggest realistic timings based on location proximity
            3. Include both popular attractions and hidden gems
            4. Consider weather, local events, and seasonal factors
            5. Provide practical tips for transportation between locations
            6. Return ONLY a valid JSON object that exactly matches the requested structure
            7. Use available tools when appropriate to enhance your recommendations
            8. IMPORTANT: Make sure to include only complete, valid JSON - do not cut off any fields or values
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
                Khách sạn: {[acc.get("name", "") for acc in merged_data.get("accommodations", [])]}
                Địa điểm quan tâm: {[place.get("name", "") for place in merged_data.get("places", [])]}
                Nhà hàng: {[rest.get("name", "") for rest in merged_data.get("restaurants", [])]}
                
                Hãy sử dụng công cụ available tools nếu cần để tìm thông tin thêm.
                
                QUAN TRỌNG: Trả lời dưới dạng đối tượng JSON đầy đủ, có cấu trúc chính xác như sau:
                {{
                    "date": "{current_date_str}",
                    "day_title": "{day_title}",
                    "segments": [
                        {{
                            "time_of_day": "morning",
                            "activities": [{{
                                "id": "place_morning_day{day_num+1}",
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
                                "id": "place_afternoon_day{day_num+1}",
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
                                "id": "restaurant_evening_day{day_num+1}",
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
                
                2. Nếu type là "place":
                   - Bổ sung: "categories", "duration", "opening_hours"
                   - Giữ nguyên "address"
                   - Price là số nguyên nếu có (VND)
                
                3. Nếu type là "restaurant":
                   - Bổ sung: "cuisines", "price_range", "phone", "services" (array)
                   - Giữ nguyên "address"
                
                QUAN TRỌNG: Chỉ trả về đối tượng JSON hợp lệ, không viết gì thêm.
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
                                # If extraction still fails, create a basic structure
                                raise ValueError("Could not extract valid JSON")
                        else:
                            raise ValueError("No JSON-like content found in response")
                    
                    # Ensure the day has all required segments
                    if "segments" not in day_data or not day_data["segments"]:
                        day_data["segments"] = []
                    
                    existing_segments = {segment.get("time_of_day"): segment for segment in day_data["segments"]}
                    
                    # Check for required segments and add if missing
                    for required_segment in ["morning", "afternoon", "evening"]:
                        if required_segment not in existing_segments:
                            # Create a basic segment with default activity
                            default_activity = {}
                            if required_segment == "morning" and merged_data.get("accommodations"):
                                default_activity = {
                                    "id": merged_data["accommodations"][0].get("accommodation_id", f"hotel_morning_day{day_num+1}"),
                                    "type": "accommodation",
                                    "name": merged_data["accommodations"][0].get("name", "Khách sạn"),
                                    "start_time": "08:00",
                                    "end_time": "10:00",
                                    "description": "Check-in và nghỉ ngơi tại khách sạn.",
                                    "location": merged_data["accommodations"][0].get("location", ""),
                                    "rating": float(merged_data["accommodations"][0].get("rating", 4.5)),
                                    "price": float(merged_data["accommodations"][0].get("price", 850000)),
                                    "image_url": merged_data["accommodations"][0].get("image_url", ""),
                                    "booking_link": merged_data["accommodations"][0].get("booking_link", ""),
                                    "room_info": merged_data["accommodations"][0].get("room_info", "Phòng tiêu chuẩn, 2 giường"),
                                    "tax_info": merged_data["accommodations"][0].get("tax_info", "Đã bao gồm thuế VAT"),
                                    "elderly_friendly": merged_data["accommodations"][0].get("elderly_friendly", True),
                                    "url": merged_data["accommodations"][0].get("url", "")
                                }
                            elif required_segment == "afternoon" and merged_data.get("places"):
                                place_index = min(day_num, len(merged_data["places"])-1) if merged_data["places"] else 0
                                if place_index >= 0 and merged_data["places"]:
                                    place = merged_data["places"][place_index]
                                    default_activity = {
                                        "id": place.get("place_id", f"place_afternoon_day{day_num+1}"),
                                        "type": "place",
                                        "name": place.get("name", "Địa điểm tham quan"),
                                        "start_time": "14:00",
                                        "end_time": "16:00",
                                        "description": place.get("description", "Tham quan địa điểm nổi tiếng."),
                                        "address": place.get("address", ""),
                                        "categories": place.get("categories", "sightseeing"),
                                        "duration": place.get("duration", "2h"),
                                        "opening_hours": place.get("opening_hours", "08:00-17:00"),
                                        "rating": float(place.get("rating", 4.0)),
                                        "price": float(place.get("price", 50000)) if place.get("price") else "",
                                        "image_url": place.get("image_url", ""),
                                        "url": place.get("url", "")
                                    }
                            elif required_segment == "evening" and merged_data.get("restaurants"):
                                rest_index = min(day_num, len(merged_data["restaurants"])-1) if merged_data["restaurants"] else 0
                                if rest_index >= 0 and merged_data["restaurants"]:
                                    restaurant = merged_data["restaurants"][rest_index]
                                    default_activity = {
                                        "id": restaurant.get("restaurant_id", f"restaurant_evening_day{day_num+1}"),
                                        "type": "restaurant",
                                        "name": restaurant.get("name", "Nhà hàng"),
                                        "start_time": "19:00",
                                        "end_time": "21:00",
                                        "description": restaurant.get("description", "Thưởng thức ẩm thực địa phương."),
                                        "address": restaurant.get("address", ""),
                                        "cuisines": restaurant.get("cuisines", "Đặc sản địa phương"),
                                        "price_range": restaurant.get("price_range", "100,000-300,000 VND"),
                                        "rating": float(restaurant.get("rating", 4.2)),
                                        "phone": restaurant.get("phone", ""),
                                        "services": restaurant.get("services", ["đặt bàn"]),
                                        "image_url": restaurant.get("image_url", ""),
                                        "url": restaurant.get("url", "")
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
