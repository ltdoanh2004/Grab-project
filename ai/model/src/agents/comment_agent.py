from typing import List, Optional
import os
import sys
import json
from pathlib import Path
from datetime import datetime
import time
import random
import logging

try:
    from openai import OpenAI
except ImportError:
    print("Warning: OpenAI package not found. Please install with: pip install openai")

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

ENV_PATH = os.path.join(parent_dir, '.env')

try:
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)
except ImportError:
    print("Warning: python-dotenv package not found. Please install with: pip install python-dotenv")

USE_MOCK_DATA = False

try:
    from vector_database import PlaceVectorDatabase, FnBVectorDatabase, HotelVectorDatabase
except ImportError as e:
    print(f"Warning: Vector database imports failed: {e}")
    print("Will use mock data instead")
    USE_MOCK_DATA = True

class CommentAgent:
    def __init__(self, use_mock_data=None):
        """Initialize the CommentAgent.
        
        Args:
            use_mock_data: Override whether to use mock data
        """
        self.use_mock_data = use_mock_data if use_mock_data is not None else USE_MOCK_DATA
        
        self.place_db = None
        self.fnb_db = None
        self.hotel_db = None
        
        self.database_connected = False
        
        self.openai_api_key = os.getenv("OPEN_API_KEY", "")
        self.client = None
        if self.openai_api_key:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")
        else:
            print(f"Warning: OPEN_API_KEY not found in {ENV_PATH}")
            
        # Initialize priority scores for different features
        self.priority_scores = {
            "place": {
                "family": 5,
                "kid": 5,
                "child": 5,
                "crowd": 4,
                "queue": 4,
                "wait": 4,
                "guide": 3,
                "tour": 3,
                "duration": 2,
                "time": 2
            },
            "restaurant": {
                "budget": 5,
                "price": 5,
                "cost": 5,
                "family": 4,
                "kid": 4,
                "child": 4,
                "authentic": 3,
                "traditional": 3,
                "atmosphere": 2,
                "ambiance": 2
            },
            "hotel": {
                "budget": 5,
                "price": 5,
                "cost": 5,
                "facilities": 4,
                "amenities": 4,
                "pool": 4,
                "kitchen": 4,
                "location": 3,
                "distance": 3,
                "design": 2,
                "style": 2
            }
        }
        
        self.query_templates = {
            "place": "{features} {place_type} in {location}",
            "restaurant": "{cuisine} restaurant in {location}: {features}",
            "hotel": "{location} hotel {price_range}: {features}"
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        if not self.use_mock_data:
            try:
                self._init_databases()
                self.database_connected = True
            except Exception as e:
                print(f"Warning: Database initialization failed: {e}")
                print("Will use mock data instead")
                self.use_mock_data = True
        
    def _init_databases(self):
        """Initialize vector databases as needed"""
        if self.use_mock_data:
            return
            
        if self.place_db is not None and self.fnb_db is not None and self.hotel_db is not None:
            return
            
        timeout = 10  # seconds
        start_time = time.time()
        
        try:
            print("Initializing vector databases...")
            
            # Initialize PlaceVectorDatabase with timeout
            if self.place_db is None:
                print("Connecting to place database...")
                self.place_db = PlaceVectorDatabase()
                if time.time() - start_time > timeout:
                    raise TimeoutError("Database connection timeout")
                self.place_db.set_up_pinecone()
            
            # Initialize FnBVectorDatabase with timeout
            if self.fnb_db is None:
                print("Connecting to restaurant database...")
                self.fnb_db = FnBVectorDatabase()
                if time.time() - start_time > timeout:
                    raise TimeoutError("Database connection timeout")
                self.fnb_db.set_up_pinecone()
                
            # Initialize HotelVectorDatabase with timeout
            if self.hotel_db is None:
                print("Connecting to hotel database...")
                self.hotel_db = HotelVectorDatabase()
                if time.time() - start_time > timeout:
                    raise TimeoutError("Database connection timeout")
                self.hotel_db.set_up_pinecone()
                
            print("All databases initialized successfully")
            
        except Exception as e:
            print(f"Database initialization error: {e}")
            print("Setting use_mock_data to True")
            self.use_mock_data = True
            raise
    
    def _generate_mock_suggestions(self, query, suggestion_type, destination="Hà Nội", count=5):
        """Generate mock suggestions when database is not available"""
        print(f"Đang tạo {suggestion_type} mẫu cho truy vấn: {query}")
        
        mock_data = {
            "place": [
                {
                    "id": "place_001117",
                    "name": "Bảo tàng Dân tộc học Việt Nam",
                    "type": "place",
                    "address": "Đường Nguyễn Văn Huyên, Cầu Giấy, Hà Nội",
                    "description": "Bảo tàng tương tác với các mô hình và hiện vật dân tộc học sống động. Có nhiều khu vực ngoài trời rộng rãi để trẻ em có thể khám phá và vui chơi.",
                    "categories": "bảo tàng, thân thiện với gia đình",
                    "opening_hours": "8:30-17:30",
                    "rating": 4.7,
                    "score": 0.92
                },
                {
                    "id": "place_000594",
                    "name": "Khu vui chơi Thiên đường Bảo Sơn",
                    "type": "place",
                    "address": "Phường An Khánh, Nam Từ Liêm, Hà Nội",
                    "description": "Khu vui chơi giải trí kết hợp với bảo tàng tương tác dành cho trẻ em, có nhiều hoạt động giáo dục và giải trí.",
                    "categories": "vui chơi, thân thiện với gia đình, tương tác",
                    "opening_hours": "8:00-17:00",
                    "rating": 4.5,
                    "score": 0.89
                },
                {
                    "id": "place_000881",
                    "name": "Bảo tàng Phụ nữ Việt Nam",
                    "type": "place",
                    "address": "36 Lý Thường Kiệt, Hoàn Kiếm, Hà Nội",
                    "description": "Bảo tàng hiện đại với nhiều khu vực tương tác, thời gian tham quan ngắn phù hợp với trẻ em và các triển lãm thân thiện với gia đình.",
                    "categories": "bảo tàng, thân thiện với gia đình, ngoài trời",
                    "opening_hours": "8:00-17:00",
                    "rating": 4.6,
                    "score": 0.87
                }
            ],
            "restaurant": [
                {
                    "id": "restaurant_001440",
                    "name": "Quán Ăn Ngon",
                    "type": "restaurant",
                    "address": "18 Phan Bội Châu, Hoàn Kiếm, Hà Nội",
                    "description": "Nhà hàng phục vụ các món ăn Việt Nam đa dạng trong không gian thoải mái, phù hợp cho gia đình với thực đơn đặc biệt cho trẻ em.",
                    "cuisines": "Việt Nam, Đặc sản địa phương",
                    "price_range": "150.000-300.000 VNĐ",
                    "rating": 4.6,
                    "score": 0.91
                },
                {
                    "id": "restaurant_000424",
                    "name": "Nhà hàng Hương Việt",
                    "type": "restaurant",
                    "address": "35 Nguyễn Thị Định, Cầu Giấy, Hà Nội",
                    "description": "Nhà hàng bình dân với các món ăn Việt Nam truyền thống, không gian thân thiện và giá cả phải chăng, phù hợp cho gia đình.",
                    "cuisines": "Việt Nam, Truyền thống",
                    "price_range": "100.000-200.000 VNĐ",
                    "rating": 4.4,
                    "score": 0.88
                }
            ],
            "hotel": [
                {
                    "id": "hotel_005950",
                    "name": "Hanoi La Siesta Hotel & Spa",
                    "type": "hotel",
                    "address": "94 Mã Mây, Hoàn Kiếm, Hà Nội",
                    "description": "Khách sạn tầm trung với phòng gia đình và vị trí thuận tiện gần các điểm tham quan. Có bếp nhỏ trong một số phòng.",
                    "amenities": "WiFi miễn phí, Phòng gia đình, Bếp nhỏ",
                    "price_per_night": 1500000,
                    "rating": 4.5,
                    "score": 0.90
                },
                {
                    "id": "hotel_001100",
                    "name": "Hanoi Emerald Waters Hotel",
                    "type": "hotel",
                    "address": "42 Hàng Bạc, Hoàn Kiếm, Hà Nội",
                    "description": "Khách sạn căn hộ với bếp nhỏ và phòng kết nối. Tuyệt vời cho gia đình muốn có không gian rộng rãi và tự nấu ăn.",
                    "amenities": "Bếp nhỏ, WiFi miễn phí, Phòng kết nối, Tiện nghi giặt ủi",
                    "price_per_night": 1200000,
                    "rating": 4.3,
                    "score": 0.87
                }
            ]
        }
        
        # Get mock data for the requested type
        type_data = mock_data.get(suggestion_type, [])
        
        # Make sure we don't try to return more items than we have
        count = min(count, len(type_data))
        
        # Modify mock data based on query
        results = []
        for item in type_data[:count]:
            # Create a copy to avoid modifying the original
            modified_item = item.copy()
            
            # Adjust score slightly based on query terms
            score_boost = 0
            for term in query.lower().split():
                if term in modified_item["name"].lower() or term in modified_item["description"].lower():
                    score_boost += 0.01
                    
            modified_item["score"] = min(1.0, modified_item["score"] + score_boost)
            
            # Ensure only necessary fields are included in the result
            processed_item = {
                "id": modified_item["id"],
                "name": modified_item["name"],
                "description": modified_item["description"],
                "type": modified_item["type"],  # Add type to ensure it's available
                "score": modified_item["score"]
            }
            
            # Add type-specific fields (but not 'type' itself)
            if suggestion_type == "restaurant":
                processed_item.update({
                    "cuisines": modified_item.get("cuisines", ""),
                    "price_range": modified_item.get("price_range", "")
                })
            elif suggestion_type == "hotel":
                processed_item.update({
                    "amenities": modified_item.get("amenities", ""),
                    "price_per_night": modified_item.get("price_per_night", 0)
                })
                
            results.append(processed_item)
            
        # Sort by score
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        
        return results
    
    def _get_suggestions_by_type(self, data, query, suggestion_type):
        """Get suggestions for a specific type"""
        self.logger.info(f"Getting suggestions for type: {suggestion_type}")
        self.logger.info(f"Query: {query}")
        suggestions = []
        
        # If using mock data, return mock suggestions
        if self.use_mock_data:
            self.logger.info("Using mock data for suggestions")
            return self._generate_mock_suggestions(query, suggestion_type, data["destination"]["id"])
        
        # Try to connect to databases if not already connected
        if not self.database_connected:
            try:
                self.logger.info("Initializing databases")
                self._init_databases()
                self.database_connected = True
            except Exception as e:
                self.logger.error(f"Failed to connect to databases: {str(e)}", exc_info=True)
                self.logger.info("Falling back to mock data")
                self.use_mock_data = True
                return self._generate_mock_suggestions(query, suggestion_type, data["destination"]["id"])
        
        # Query actual databases
        self.logger.info(f"Querying {suggestion_type} database")
        try:
            if suggestion_type == "restaurant":
                self.logger.info("Querying restaurant database")
                fnb_ids, fnb_results = self.fnb_db.query(query, filter=self.filter, top_k=10)
                self.logger.info(f"Received {len(fnb_results)} restaurant results")
                
                for match in fnb_results:
                    try:
                        suggestions.append({
                            "id": match["id"],
                            "name": match["metadata"].get("name", ""),
                            "description": match["metadata"].get("description", ""),
                            "cuisines": match["metadata"].get("cuisines", ""),
                            "price_range": match["metadata"].get("price_range", ""),
                            "rating": match["metadata"].get("rating", 0),
                            "score": match["score"]
                        })
                    except Exception as e:
                        self.logger.error(f"Error processing restaurant match: {str(e)}", exc_info=True)
                        continue
                    
            elif suggestion_type == "place":
                self.logger.info("Querying place database")
                place_ids, place_results = self.place_db.query(query, filter=self.filter, top_k=10)
                self.logger.info(f"Received {len(place_results)} place results")
                
                for match in place_results:
                    try:
                        suggestions.append({
                            "id": match["id"],
                            "name": match["metadata"].get("name", ""),
                            "description": match["metadata"].get("description", ""),
                            "rating": match["metadata"].get("rating", 0),
                            "score": match["score"]
                        })
                    except Exception as e:
                        self.logger.error(f"Error processing place match: {str(e)}", exc_info=True)
                        continue
                    
            elif suggestion_type == "hotel":
                self.logger.info("Querying hotel database")
                hotel_ids, hotel_results = self.hotel_db.query(query, filter=self.filter, top_k=10)
                self.logger.info(f"Received {len(hotel_results)} hotel results")
                
                for match in hotel_results:
                    try:
                        suggestions.append({
                            "id": match["id"],
                            "name": match["metadata"].get("name", ""),
                            "description": match["metadata"].get("description", ""),
                            "amenities": match["metadata"].get("amenities", ""),
                            "price_per_night": match["metadata"].get("price_per_night", 0),
                            "rating": match["metadata"].get("rating", 0),
                            "score": match["score"]
                        })
                    except Exception as e:
                        self.logger.error(f"Error processing hotel match: {str(e)}", exc_info=True)
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error querying database for {suggestion_type}: {str(e)}", exc_info=True)
            self.logger.info("Falling back to mock data")
            return self._generate_mock_suggestions(query, suggestion_type, data["destination"]["id"])
        
        # If no results from database, use mock data
        if not suggestions:
            self.logger.warning(f"No results from database for {suggestion_type}. Using mock data.")
            return self._generate_mock_suggestions(query, suggestion_type, data["destination"]["id"])
            
        self.logger.info(f"Returning {len(suggestions)} suggestions for {suggestion_type}")
        return sorted(suggestions, key=lambda x: x.get("score", 0), reverse=True)

    def gen_activity_comment(self, comment_plan: dict):
        self.logger.info(f"Received trip plan request: {comment_plan}")
        self.destination_id = comment_plan.get("destination_id", "")
        self.filter = {"city": {"$eq" : self.destination_id}}
        
        budget = comment_plan.get("budget", {})
        budget_type = budget.get("type", "") if isinstance(budget, dict) else ""
        exact_budget = budget.get("exact_budget", 0) if isinstance(budget, dict) else 0
        
        people = comment_plan.get("people", {})
        adults = people.get("adults", 0) if isinstance(people, dict) else 0
        children = people.get("children", 0) if isinstance(people, dict) else 0
        infants = people.get("infants", 0) if isinstance(people, dict) else 0
        pets = people.get("pets", 0) if isinstance(people, dict) else 0
        
        travel_time = comment_plan.get("travel_time", {})
        travel_time_type = travel_time.get("type", "") if isinstance(travel_time, dict) else ""
        start_date = travel_time.get("start_date", "") if isinstance(travel_time, dict) else ""
        end_date = travel_time.get("end_date", "") if isinstance(travel_time, dict) else ""
        
        personal_options = comment_plan.get("personal_options", [])
        activities = []
        cuisines = []
        
        for option in personal_options:
            option_type = option.get("type", "")
            option_name = option.get("name", "")
            option_description = option.get("description", "")
            
            if option_type == "activity":
                activities.append({
                    "name": option_name,
                    "description": option_description
                })
            elif option_type == "cuisine":
                cuisines.append({
                    "name": option_name,
                    "description": option_description
                })
        
        activity = comment_plan.get("activity", {})
        activity_id = activity.get("activity_id", "")
        place_id = activity.get("id", "")
        activity_type = activity.get("type", "")
        activity_name = activity.get("name", "")
        activity_start_time = activity.get("start_time", "")
        activity_end_time = activity.get("end_time", "")
        activity_description = activity.get("description", "")
        
        activity_comments = activity.get("comments", [])
        parsed_comments = []
        
        for comment in activity_comments:
            parsed_comments.append({
                "user_id": comment.get("user_id", ""),
                "comment_message": comment.get("comment_message", ""),
                "trip_place_id": comment.get("trip_place_id", "")
            })
        
        structured_data = {
            "destination": {
                "id": self.destination_id
            },
            "budget": {
                "type": budget_type,
                "amount": exact_budget
            },
            "group": {
                "adults": adults,
                "children": children,
                "infants": infants,
                "pets": pets,
                "total": adults + children + infants + pets
            },
            "duration": {
                "type": travel_time_type,
                "start_date": start_date,
                "end_date": end_date
            },
            "preferences": {
                "activities": activities,
                "cuisines": cuisines
            },
            "current_activity": {
                "id": activity_id,
                "place_id": place_id,
                "type": activity_type,
                "name": activity_name,
                "time": {
                    "start": activity_start_time,
                    "end": activity_end_time
                },
                "description": activity_description,
                "comments": parsed_comments
            }
        }
        
        suggestion_type = self._determine_suggestion_type(structured_data)
        query_context = self._generate_llm_query_for_type(structured_data, suggestion_type)
        suggestions = self._get_suggestions_by_type(structured_data, query_context, suggestion_type)
        
        # Prepare enhanced suggestion list
        suggestion_list = self._prepare_suggestion_list(suggestions, structured_data)
        
        return {
            "suggestion_type": suggestion_type,
            "suggestion_list": suggestion_list,
            "query_used": query_context
        }
    
    def _determine_suggestion_type(self, data):
        """Determine which type of suggestion to return based on user context"""
        current_type = data["current_activity"].get("type", "").lower()
        
        if current_type in ["restaurant", "food", "fnb"]:
            return "restaurant"
        elif current_type in ["hotel", "accommodation"]:
            return "hotel"
        elif current_type in ["place", "attraction"]:
            return "place"
        
        if len(data["preferences"]["cuisines"]) > 0:
            return "restaurant"
        
        if data["duration"].get("start_date") and data["duration"].get("end_date"):
            try:
                start = datetime.fromisoformat(data["duration"]["start_date"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(data["duration"]["end_date"].replace("Z", "+00:00"))
                days = (end - start).days
                if days >= 1:
                    return "hotel"
            except:
                pass
        
        return "place"
    
    def _analyze_comment_intentions(self, comments):
        """Enhanced comment analysis to better understand user's change intentions"""
        if not comments:
            return {
                "pain_points": [],
                "desired_features": [],
                "constraints": [],
                "retain_features": []
            }
            
        try:
            self._initialize_llm()
            
            system_message = """
            Bạn là một chuyên gia phân tích và đề xuất về du lịch, phân tích bình luận của người dùng để hiểu những thay đổi họ mong muốn.
            Tập trung vào các khía cạnh chính:
            1. Điểm đau hiện tại:
               - Họ đang gặp vấn đề cụ thể gì?
               - Những khía cạnh nào họ không hài lòng?
            
            2. Thay đổi mong muốn:
               - Họ muốn cải thiện cụ thể điều gì?
               - Họ đang tìm kiếm tính năng gì?
            
            3. Các ràng buộc:
               - Hạn chế về ngân sách
               - Ràng buộc về thời gian
               - Nhu cầu đặc biệt của nhóm (gia đình, trẻ em, v.v.)
               - Ưu tiên về vị trí
            
            4. Tính năng cần giữ lại:
               - Những khía cạnh tích cực nào cần được duy trì?
               - Những tính năng nào họ vẫn muốn giữ?

            Trả về đối tượng JSON với các trường sau:
            {
                "pain_points": ["danh sách các vấn đề cụ thể"],
                "desired_features": ["danh sách các tính năng mong muốn"],
                "constraints": ["danh sách các ràng buộc"],
                "retain_features": ["danh sách các tính năng cần giữ lại"]
            }
            """
            
            # Prepare comments for analysis
            comment_text = " | ".join([
                comment.get("comment_message", "")
                for comment in comments
                if comment.get("comment_message")
            ])
            
            if not comment_text:
                return {
                    "pain_points": [],
                    "desired_features": [],
                    "constraints": [],
                    "retain_features": []
                }
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Phân tích các bình luận này để tìm yêu cầu thay đổi: {comment_text}"}
                ],
                response_format={"type": "json_object"}
            )
            
            try:
                analysis = json.loads(response.choices[0].message.content)
                return analysis
            except Exception as je:
                print(f"Error parsing JSON from LLM: {je}")
                basic_intentions = self._extract_basic_intentions(comments)
                return {
                    "pain_points": basic_intentions,
                    "desired_features": basic_intentions,
                    "constraints": [],
                    "retain_features": []
                }
                
        except Exception as e:
            print(f"Error analyzing comment intentions: {e}")
            basic_intentions = self._extract_basic_intentions(comments)
            return {
                "pain_points": basic_intentions,
                "desired_features": basic_intentions,
                "constraints": [],
                "retain_features": []
            }

    def _optimize_query_length(self, query, max_length=100):
        """Optimize query length for vector search"""
        if len(query) <= max_length:
            return query
            
        # Split into key phrases
        phrases = [p.strip() for p in query.split(',')]
        
        # Start with high priority phrases
        essential_phrases = []
        other_phrases = []
        
        for phrase in phrases:
            if any(key in phrase.lower() for key in ['budget', 'price', 'family', 'kid', 'child', 'location']):
                essential_phrases.append(phrase)
            else:
                other_phrases.append(phrase)
        
        # Combine phrases while respecting max length
        optimized_query = ''
        
        # Add essential phrases first
        for phrase in essential_phrases:
            if len(optimized_query) + len(phrase) + 2 <= max_length:
                optimized_query += (', ' if optimized_query else '') + phrase
                
        # Add other phrases if space allows
        for phrase in other_phrases:
            if len(optimized_query) + len(phrase) + 2 <= max_length:
                optimized_query += (', ' if optimized_query else '') + phrase
            else:
                break
                
        return optimized_query

    def _prioritize_features(self, features, suggestion_type):
        """Score and prioritize features based on type"""
        scored_features = []
        
        for feature in features:
            score = 0
            feature_lower = feature.lower()
            
            # Check against priority scores for the suggestion type
            for key, value in self.priority_scores[suggestion_type].items():
                if key in feature_lower:
                    score = max(score, value)  # Take highest matching score
            
            scored_features.append((score, feature))
        
        # Sort by score and return features
        return [f[1] for f in sorted(scored_features, reverse=True)]

    def _generate_llm_query_for_type(self, data, suggestion_type):
        """Generate optimized search query based on comment analysis"""
        try:
            self._initialize_llm()
            
            # Analyze comments
            comment_analysis = self._analyze_comment_intentions(data["current_activity"].get("comments", []))
            
            # Prioritize features from analysis
            pain_points = self._prioritize_features(comment_analysis.get('pain_points', []), suggestion_type)
            desired_features = self._prioritize_features(comment_analysis.get('desired_features', []), suggestion_type)
            constraints = self._prioritize_features(comment_analysis.get('constraints', []), suggestion_type)
            retain_features = self._prioritize_features(comment_analysis.get('retain_features', []), suggestion_type)
            
            # Prepare template variables
            template_vars = {
                "location": data["destination"]["id"],
                "features": "",
                "place_type": data["current_activity"]["type"],
                "cuisine": "French" if suggestion_type == "restaurant" else "",
                "price_range": ""
            }
            
            # Build features string
            feature_parts = []
            
            # Add constraints (especially budget) first
            for constraint in constraints:
                if "budget" in constraint.lower() or "price" in constraint.lower():
                    template_vars["price_range"] = constraint
                else:
                    feature_parts.append(constraint)
            
            # Add high-priority features
            feature_parts.extend(desired_features[:3])  # Top 3 desired features
            
            # Add retain features if space allows
            if retain_features:
                feature_parts.append(f"maintaining {retain_features[0]}")
            
            template_vars["features"] = ", ".join(feature_parts)
            
            # Get and fill template
            template = self.query_templates.get(suggestion_type, "{features} in {location}")
            query = template.format(**template_vars)
            
            # Optimize query length
            optimized_query = self._optimize_query_length(query)
            
            return optimized_query
            
        except Exception as e:
            print(f"Error generating LLM query: {e}")
            return self._build_fallback_query(data, suggestion_type)

    def _build_fallback_query(self, data, suggestion_type):
        """Enhanced fallback query builder with better context understanding"""
        query_parts = []
        
        analysis = self._extract_basic_intentions(data["current_activity"].get("comments", []))
        
        prioritized_intentions = self._prioritize_features(analysis, suggestion_type)
        
        if data["current_activity"]["name"]:
            query_parts.append(f"alternative to {data['current_activity']['name']}")
        
        if prioritized_intentions:
            query_parts.extend(prioritized_intentions[:3])  # Add top 3 prioritized intentions
        
        if suggestion_type == "restaurant":
            if any("budget" in i.lower() for i in prioritized_intentions):
                query_parts.append("affordable")
            if any("family" in i.lower() for i in prioritized_intentions):
                query_parts.append("family-friendly")
            if any("authentic" in i.lower() for i in prioritized_intentions):
                query_parts.append("authentic local")
                
        elif suggestion_type == "place":
            if any("crowd" in i.lower() for i in prioritized_intentions):
                query_parts.append("less crowded")
            if any(word in str(prioritized_intentions).lower() for word in ["kid", "child", "family"]):
                query_parts.append("family-friendly interactive")
            if any("guide" in i.lower() for i in prioritized_intentions):
                query_parts.append("guided tours")
                
        elif suggestion_type == "hotel":
            if any("budget" in i.lower() for i in prioritized_intentions):
                query_parts.append("moderate price")
            if any("family" in i.lower() for i in prioritized_intentions):
                query_parts.append("family-friendly")
            if any(word in str(prioritized_intentions).lower() for word in ["facility", "amenity", "pool"]):
                query_parts.append("good amenities")
        
        # Add location context
        if data["destination"]["id"]:
            query_parts.append(f"in {data['destination']['id']}")
        
        # Optimize query length
        query = " ".join(query_parts)
        return self._optimize_query_length(query)

    def _extract_basic_intentions(self, comments):
        """Enhanced basic keyword analysis with better context understanding"""
        # Define comprehensive change indicators with their contexts
        change_indicators = {
            # Budget-related
            "expensive": "lower price",
            "costly": "more affordable",
            "pricey": "budget friendly",
            "over budget": "within budget",
            "€": "price consideration",
            
            # Family-related
            "kids": "family friendly",
            "children": "child appropriate",
            "family": "family oriented",
            "baby": "infant friendly",
            
            # Comfort/Convenience
            "crowded": "less crowded",
            "busy": "quieter",
            "noisy": "peaceful",
            "queue": "shorter wait",
            "waiting": "better access",
            
            # Facilities
            "pool": "with pool",
            "kitchen": "with kitchen",
            "parking": "with parking",
            "wifi": "with wifi",
            
            # Experience
            "authentic": "authentic experience",
            "traditional": "traditional style",
            "modern": "contemporary",
            "guide": "guided experience",
            
            # Location
            "far": "better located",
            "distance": "convenient location",
            "location": "good location",
            "central": "centrally located"
        }
        
        intentions = []
        
        for comment in comments:
            message = comment.get("comment_message", "").lower()
            if not message:
                continue
            
            # Split into sentences for better context
            sentences = message.split(".")
            
            for sentence in sentences:
                words = sentence.split()
                
                # Look for change indicators and their context
                for indicator, meaning in change_indicators.items():
                    if indicator in sentence:
                        # Get the surrounding context (words before and after the indicator)
                        idx = sentence.find(indicator)
                        context_start = max(0, idx - 30)
                        context_end = min(len(sentence), idx + 30)
                        context = sentence[context_start:context_end].strip()
                        
                        # Add both the meaning and the context
                        intentions.append(f"{meaning} ({context})")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_intentions = []
        for item in intentions:
            if item not in seen:
                seen.add(item)
                unique_intentions.append(item)
        
        return unique_intentions

    def _generate_description(self, suggestion, data):
        """Generate an enhanced description for the suggestion"""
        # Get the base description first to ensure it exists
        base_description = suggestion.get("description", "")
        if not base_description or len(base_description) < 20:
            base_description = f"{suggestion.get('name', '')} ở {data['destination']['id']}"
            
        try:
            self._initialize_llm()
            
            # Get suggestion type safely
            suggestion_type = suggestion.get("type", data.get("suggestion_type", "place"))
            
            prompt = f"""
            Tạo một mô tả hấp dẫn và nhiều thông tin cho {suggestion_type} này ở {data['destination']['id']}.
            Tên: {suggestion.get('name', '')}
            Mô tả hiện tại: {base_description}
            
            Tập trung vào:
            1. Các tính năng độc đáo và điều gì làm nó đặc biệt
            2. Tại sao nó là một lựa chọn thay thế tốt cho {data['current_activity']['name']}
            3. Nó giải quyết những mối quan tâm được nêu trong bình luận của người dùng như thế nào
            
            Hãy viết ngắn gọn (khoảng 200-250 từ), hấp dẫn, và nhấn mạnh các tính năng phù hợp với sở thích của người dùng.
            Không sử dụng ngôn ngữ quảng cáo hoặc phóng đại. Đảm bảo đầy đủ các ý.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Bạn là chuyên gia du lịch tạo ra các mô tả chính xác và hữu ích bằng tiếng Việt."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating description: {e}")
            return base_description
    
    def _estimate_price(self, suggestion, data):
        """Estimate the price for a specific activity based on its type and other details"""
        if "price_per_night" in suggestion:
            return float(suggestion["price_per_night"])
        elif "price" in suggestion:
            return float(suggestion["price"])
        
        try:
            self._initialize_llm()
            
            # Extract budget info from user data
            budget_info = ""
            if data["budget"]["amount"] > 0:
                budget_info = f"Ngân sách của người dùng khoảng {data['budget']['amount']} ({data['budget']['type']})"
            
            # Determine suggestion type from either the suggestion or from data
            suggestion_type = suggestion.get("type", data.get("suggestion_type", "place"))
            
            prompt = f"""
            Ước tính một mức giá hợp lý cho {suggestion_type} này ở {data['destination']['id']}:
            Tên: {suggestion['name']}
            Mô tả: {suggestion['description']}
            
            {budget_info}
            
            Chỉ trả về một số (không có văn bản) thể hiện:
            - Đối với khách sạn: giá mỗi đêm theo đơn vị tiền tệ của {data['destination']['id']}
            - Đối với nhà hàng: giá trung bình mỗi người theo đơn vị tiền tệ của {data['destination']['id']}
            - Đối với địa điểm/điểm tham quan: phí vào cửa hoặc chi phí điển hình theo đơn vị tiền tệ của {data['destination']['id']}
            
            Ví dụ: 250000
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Bạn là chuyên gia về giá cả du lịch. Chỉ trả lời bằng một con số."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10
            )
            
            price_str = response.choices[0].message.content.strip()
            price_str = ''.join(c for c in price_str if c.isdigit())
            if price_str:
                return float(price_str)
            return 0.0
            
        except Exception as e:
            print(f"Error estimating price: {e}")
            return 0.0

    def _prepare_suggestion_list(self, suggestions, data):
        """Prepare the suggestion list with enhanced data"""
        suggestion_list = []
        suggestion_type = data.get("suggestion_type", "place")
        
        for suggestion in suggestions:
            # Get suggestion type safely
            item_type = suggestion.get("type", suggestion_type)
            
            # Add the type to the suggestion for _generate_description to use
            suggestion_with_type = suggestion.copy()
            if "type" not in suggestion_with_type:
                suggestion_with_type["type"] = item_type
                
            enhanced_description = self._generate_description(suggestion_with_type, data)
            price_estimate = self._estimate_price(suggestion, data)
            
            # Create base suggestion item with common fields
            suggestion_item = {
                "id": suggestion["id"],
                "name": suggestion["name"],
                "description": enhanced_description,
                "price_ai_estimate": price_estimate
            }
            
            # Add type-specific fields based on item_type
            if item_type == "restaurant":
                suggestion_item.update({
                    "cuisines": suggestion.get("cuisines", ""),
                    "price_range": suggestion.get("price_range", "")
                })
            elif item_type == "hotel":
                suggestion_item.update({
                    "amenities": suggestion.get("amenities", ""),
                    "price_per_night": suggestion.get("price_per_night", price_estimate)
                })
            
            suggestion_list.append(suggestion_item)
            
        return suggestion_list

    def _initialize_llm(self):
        """Initialize the OpenAI client if not already initialized."""
        if self.client is not None:
            return
        
        # Try to initialize the client
        self.openai_api_key = os.getenv("OPEN_API_KEY", "")
        if not self.openai_api_key:
            print(f"Warning: OPEN_API_KEY not found in {ENV_PATH}")
            raise ValueError("OpenAI API key not found")
            
        try:
            self.client = OpenAI(api_key=self.openai_api_key)
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            raise

def main():
    # Base test data with common fields in Vietnamese
    base_data = {
        "destination_id": "Hà Nội",
        "budget": {
            "type": "linh hoạt",
            "exact_budget": 2000000
        },
        "people": {
            "adults": 2,
            "children": 1,
            "infants": 0,
            "pets": 0
        },
        "travel_time": {
            "type": "cố định",
            "start_date": "2025-06-01T00:00:00Z",
            "end_date": "2025-06-10T00:00:00Z"
        },
        "personal_options": []  # Initial preferences will be empty as we want suggestions based on comments
    }

    # Test Case 1: User wants to change their museum activity (Vietnamese)
    place_data = base_data.copy()
    place_data["activity"] = {
        "activity_id": "act_123",
        "id": "place_000481",
        "type": "place",
        "name": "Bảo tàng Lịch sử Quốc gia",
        "start_time": "10:30",
        "end_time": "14:00",
        "description": "Bảo tàng lưu giữ và trưng bày các hiện vật lịch sử qua các thời kỳ của Việt Nam.",
        "comments": [
            {
                "user_id": "user123",
                "comment_message": "Bảo tàng rất đẹp nhưng quá tĩnh lặng và thiếu các hoạt động tương tác cho trẻ em. Con tôi chán và mệt sau 30 phút. Chúng tôi cần một bảo tàng thân thiện với gia đình hơn, có các triển lãm tương tác và thời gian tham quan ngắn hơn.",
                "trip_place_id": "place_000481"
            },
            {
                "user_id": "user456",
                "comment_message": "Các hiện vật rất giá trị nhưng cách trưng bày không hấp dẫn trẻ em. Chúng tôi muốn một nơi nào đó vui nhộn hơn mà vẫn mang tính giáo dục cho cả gia đình.",
                "trip_place_id": "place_000481"
            }
        ]
    }

    # Test Case 2: User wants to change their dining experience (Vietnamese)
    restaurant_data = base_data.copy()
    restaurant_data["activity"] = {
        "activity_id": "act_456",
        "id": "rest_000789",
        "type": "restaurant",
        "name": "Nhà hàng Sen Tây Hồ",
        "start_time": "19:30",
        "end_time": "21:30",
        "description": "Nhà hàng cao cấp phục vụ ẩm thực Việt Nam truyền thống với không gian sang trọng",
        "comments": [
            {
                "user_id": "user789",
                "comment_message": "Thức ăn ngon nhưng không gian quá trang trọng cho bữa tối gia đình. Chúng tôi muốn ăn đồ Việt Nam ngon nhưng trong một không gian thoải mái hơn, nơi trẻ em không làm phiền người khác. Có lẽ một quán bình dân?",
                "trip_place_id": "rest_000789"
            },
            {
                "user_id": "user101",
                "comment_message": "Dịch vụ tốt nhưng 1.500.000 đồng cho bữa tối quá đắt cho gia đình chúng tôi. Tôi muốn tìm một lựa chọn phải chăng hơn mà vẫn có hương vị Việt Nam đích thực.",
                "trip_place_id": "rest_000789"
            }
        ]
    }

    # Test Case 3: User wants to change their accommodation (Vietnamese)
    hotel_data = base_data.copy()
    hotel_data["activity"] = {
        "activity_id": "act_789",
        "id": "hotel_000123",
        "type": "hotel",
        "name": "Khách sạn Metropole Hà Nội",
        "start_time": "",
        "end_time": "",
        "description": "Khách sạn 5 sao sang trọng tại trung tâm Hà Nội",
        "comments": [
            {
                "user_id": "user202",
                "comment_message": "Khách sạn này quá đắt cho chuyến đi 9 ngày của chúng tôi. Chúng tôi cần một lựa chọn phải chăng hơn nhưng vẫn muốn ở gần các điểm tham quan chính. Khoảng 1-2 triệu đồng mỗi đêm sẽ phù hợp hơn.",
                "trip_place_id": "hotel_000123"
            },
            {
                "user_id": "user303",
                "comment_message": "Phòng đẹp nhưng không thực tế cho gia đình chúng tôi. Chúng tôi cần một khách sạn có bếp nhỏ và có thể là phòng kết nối. Cũng muốn có hồ bơi hoặc khu vui chơi cho trẻ em.",
                "trip_place_id": "hotel_000123"
            }
        ]
    }

    # Initialize agent
    agent = CommentAgent(use_mock_data=True)  # Force using mock data for testing

    print("\nKiểm tra Đề xuất Địa điểm:")
    print("Kịch bản: Gia đình muốn thay đổi từ Bảo tàng sang nơi thân thiện với trẻ em hơn")
    place_result = agent.gen_activity_comment(place_data)
    print(json.dumps(place_result, indent=2, ensure_ascii=False))

    print("\nKiểm tra Đề xuất Nhà hàng:")
    print("Kịch bản: Gia đình tìm kiếm trải nghiệm ẩm thực Việt Nam thoải mái, giá cả phải chăng hơn")
    restaurant_result = agent.gen_activity_comment(restaurant_data)
    print(json.dumps(restaurant_result, indent=2, ensure_ascii=False))

    print("\nKiểm tra Đề xuất Khách sạn:")
    print("Kịch bản: Gia đình cần chỗ ở giá cả phải chăng, thân thiện với gia đình hơn")
    hotel_result = agent.gen_activity_comment(hotel_data)
    print(json.dumps(hotel_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

    
