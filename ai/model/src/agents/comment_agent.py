from typing import List, Optional
import os
import sys
import json
from pathlib import Path
from datetime import datetime
import time
import random

try:
    from openai import OpenAI
except ImportError:
    print("Warning: OpenAI package not found. Please install with: pip install openai")

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Set up .env path
ENV_PATH = os.path.join(parent_dir, '.env')

# Import after setting path
try:
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)
except ImportError:
    print("Warning: python-dotenv package not found. Please install with: pip install python-dotenv")

# Flag to use mock data when database is unavailable
USE_MOCK_DATA = False

# Try importing vector database modules
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
        # Set mock data flag
        self.use_mock_data = use_mock_data if use_mock_data is not None else USE_MOCK_DATA
        
        # Initialize vector databases
        self.place_db = None
        self.fnb_db = None
        self.hotel_db = None
        
        # Initialize connection flag
        self.database_connected = False
        
        # Initialize OpenAI client
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
        
        # Initialize query templates
        self.query_templates = {
            "place": "{features} {place_type} in {location}",
            "restaurant": "{cuisine} restaurant in {location}: {features}",
            "hotel": "{location} hotel {price_range}: {features}"
        }
        
        # Lazy initialize databases to avoid connection errors
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
        # Skip if using mock data
        if self.use_mock_data:
            return
            
        # Check if databases are already initialized
        if self.place_db is not None and self.fnb_db is not None and self.hotel_db is not None:
            return
            
        # Initialize with connection timeout
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
    
    def _generate_mock_suggestions(self, query, suggestion_type, destination="Paris", count=5):
        """Generate mock suggestions when database is not available"""
        print(f"Generating mock {suggestion_type} suggestions for query: {query}")
        
        mock_data = {
            "place": [
                {
                    "id": "place_001117",
                    "name": "Musée de l'Orangerie",
                    "type": "place",
                    "address": "Jardin des Tuileries, 75001 Paris, France",
                    "description": "A small museum with Monet's Water Lilies and other impressionist masterpieces, perfect for a shorter family visit.",
                    "categories": "art museum, family-friendly",
                    "opening_hours": "9:00-18:00",
                    "rating": 4.7,
                    "score": 0.92
                },
                {
                    "id": "place_000594",
                    "name": "Cité des Enfants",
                    "type": "place",
                    "address": "30 Avenue Corentin Cariou, 75019 Paris, France",
                    "description": "Interactive science museum designed especially for children with hands-on exhibits and activities.",
                    "categories": "science museum, family-friendly, interactive",
                    "opening_hours": "10:00-18:00",
                    "rating": 4.8,
                    "score": 0.89
                },
                {
                    "id": "place_000881",
                    "name": "Jardin d'Acclimatation",
                    "type": "place",
                    "address": "Bois de Boulogne, 75116 Paris, France",
                    "description": "Amusement park with rides, petting zoo and beautiful gardens, ideal for families with children.",
                    "categories": "amusement park, family-friendly, outdoors",
                    "opening_hours": "10:00-19:00",
                    "rating": 4.5,
                    "score": 0.87
                }
            ],
            "restaurant": [
                {
                    "id": "restaurant_001440",
                    "name": "Le Petit Prince",
                    "type": "restaurant",
                    "address": "12 Rue de Buci, 75006 Paris, France",
                    "description": "Charming bistro with authentic French cuisine in a relaxed setting. Perfect for families with a special children's menu.",
                    "cuisines": "French, Traditional",
                    "price_range": "€15-30",
                    "rating": 4.6,
                    "score": 0.91
                },
                {
                    "id": "restaurant_000424",
                    "name": "Chez Janou",
                    "type": "restaurant",
                    "address": "2 Rue Roger Verlomme, 75003 Paris, France",
                    "description": "Casual bistro with Provençal dishes and a friendly atmosphere. Reasonable prices and welcoming to families.",
                    "cuisines": "French, Mediterranean",
                    "price_range": "€20-35",
                    "rating": 4.4,
                    "score": 0.88
                }
            ],
            "hotel": [
                {
                    "id": "hotel_005950",
                    "name": "Hôtel des Grands Boulevards",
                    "type": "hotel",
                    "address": "17 Boulevard Poissonnière, 75002 Paris, France",
                    "description": "Charming mid-range hotel with family rooms and convenient location near attractions. Offers kitchenette in some rooms.",
                    "amenities": "Free WiFi, Family Rooms, Kitchenette",
                    "price_per_night": 220,
                    "rating": 4.5,
                    "score": 0.90
                },
                {
                    "id": "hotel_001100",
                    "name": "Citadines Les Halles Paris",
                    "type": "hotel",
                    "address": "4 Rue des Innocents, 75001 Paris, France",
                    "description": "Apartment-hotel with kitchenettes and connecting rooms. Great for families looking for more space and self-catering options.",
                    "amenities": "Kitchenette, Free WiFi, Connecting Rooms, Laundry Facilities",
                    "price_per_night": 180,
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
        suggestions = []
        
        # If using mock data, return mock suggestions
        if self.use_mock_data:
            return self._generate_mock_suggestions(query, suggestion_type, data["destination"]["id"])
        
        # Try to connect to databases if not already connected
        if not self.database_connected:
            try:
                self._init_databases()
                self.database_connected = True
            except Exception as e:
                print(f"Failed to connect to databases: {e}")
                print("Using mock data instead")
                self.use_mock_data = True
                return self._generate_mock_suggestions(query, suggestion_type, data["destination"]["id"])
        
        # Query actual databases
        try:
            if suggestion_type == "restaurant":
                fnb_ids, fnb_results = self.fnb_db.query(query, top_k=10)
                for match in fnb_results.get("matches", []):
                    suggestions.append({
                        "id": match["id"],
                        "name": match["metadata"].get("name", ""),
                        "description": match["metadata"].get("description", ""),
                        "cuisines": match["metadata"].get("cuisines", ""),
                        "price_range": match["metadata"].get("price_range", ""),
                        "rating": match["metadata"].get("rating", 0),
                        "score": match["score"]
                    })
                    
            elif suggestion_type == "place":
                place_ids, place_results = self.place_db.query(query, top_k=10)
                for match in place_results.get("matches", []):
                    suggestions.append({
                        "id": match["id"],
                        "name": match["metadata"].get("name", ""),
                        "description": match["metadata"].get("description", ""),
                        "rating": match["metadata"].get("rating", 0),
                        "score": match["score"]
                    })
                    
            elif suggestion_type == "hotel":
                hotel_ids, hotel_results = self.hotel_db.query(query, top_k=10)
                for match in hotel_results.get("matches", []):
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
            print(f"Error querying database for {suggestion_type}: {e}")
            print("Falling back to mock data")
            return self._generate_mock_suggestions(query, suggestion_type, data["destination"]["id"])
        
        # If no results from database, use mock data
        if not suggestions:
            print(f"No results from database for {suggestion_type}. Using mock data.")
            return self._generate_mock_suggestions(query, suggestion_type, data["destination"]["id"])
            
        return sorted(suggestions, key=lambda x: x.get("score", 0), reverse=True)

    def gen_activity_comment(self, comment_plan: dict):
        destination_id = comment_plan.get("destination_id", "")
        
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
                "id": destination_id
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
            
            prompt = f"""
            Tạo một mô tả hấp dẫn và nhiều thông tin cho {suggestion['type']} này ở {data['destination']['id']}.
            Tên: {suggestion['name']}
            Mô tả hiện tại: {base_description}
            
            Tập trung vào:
            1. Các tính năng độc đáo và điều gì làm nó đặc biệt
            2. Tại sao nó là một lựa chọn thay thế tốt cho {data['current_activity']['name']}
            3. Nó giải quyết những mối quan tâm được nêu trong bình luận của người dùng như thế nào
            
            Hãy viết ngắn gọn (70-100 từ), hấp dẫn, và nhấn mạnh các tính năng phù hợp với sở thích của người dùng.
            Không sử dụng ngôn ngữ quảng cáo hoặc phóng đại.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Bạn là chuyên gia du lịch tạo ra các mô tả chính xác và hữu ích bằng tiếng Việt."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating description: {e}")
            return base_description
    
    def _estimate_price(self, suggestion, data):
        """Estimate the price for a specific activity based on its type and other details"""
        # Check for existing price data first
        if suggestion["type"] == "hotel" and suggestion.get("price_per_night"):
            return float(suggestion["price_per_night"])
        elif suggestion.get("price"):
            return float(suggestion["price"])
        
        try:
            self._initialize_llm()
            
            # Extract budget info from user data
            budget_info = ""
            if data["budget"]["amount"] > 0:
                budget_info = f"Ngân sách của người dùng khoảng {data['budget']['amount']} ({data['budget']['type']})"
            
            prompt = f"""
            Ước tính một mức giá hợp lý cho {suggestion['type']} này ở {data['destination']['id']}:
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
        
        for suggestion in suggestions:
            enhanced_description = self._generate_description(suggestion, data)
            price_estimate = self._estimate_price(suggestion, data)
            
            # Chỉ bao gồm các trường cơ bản, loại bỏ type, categories, opening_hours, address
            suggestion_item = {
                "id": suggestion["id"],
                "name": suggestion["name"],
                "description": enhanced_description,
                "price_ai_estimate": price_estimate
            }
            
            # Thêm các trường cụ thể theo loại nếu cần (nhưng không thêm type)
            if suggestion["type"] == "restaurant":
                suggestion_item.update({
                    "cuisines": suggestion.get("cuisines", ""),
                    "price_range": suggestion.get("price_range", "")
                })
            elif suggestion["type"] == "hotel":
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
    # Base test data with common fields
    base_data = {
        "destination_id": "Paris",
        "budget": {
            "type": "flexible",
            "exact_budget": 1500
        },
        "people": {
            "adults": 2,
            "children": 1,
            "infants": 0,
            "pets": 0
        },
        "travel_time": {
            "type": "fixed",
            "start_date": "2025-06-01T00:00:00Z",
            "end_date": "2025-06-10T00:00:00Z"
        },
        "personal_options": []  # Initial preferences will be empty as we want suggestions based on comments
    }

    # Test Case 1: User wants to change their museum activity
    place_data = base_data.copy()
    place_data["activity"] = {
        "activity_id": "act_123",
        "id": "place_000481",
        "type": "place",
        "name": "Louvre Museum",
        "start_time": "10:30",
        "end_time": "14:00",
        "description": "World's largest art museum and historic monument.",
        "comments": [
            {
                "user_id": "user123",
                "comment_message": "The Louvre is amazing but it's way too crowded for our family. The kids got tired quickly. We need a more family-friendly museum with interactive exhibits and shorter tour duration.",
                "trip_place_id": "place_000481"
            },
            {
                "user_id": "user456",
                "comment_message": "The art is incredible but we spent most time waiting in queues. Would prefer a smaller museum where we can actually enjoy the art without rushing.",
                "trip_place_id": "place_000481"
            }
        ]
    }

    # Test Case 2: User wants to change their dining experience
    restaurant_data = base_data.copy()
    restaurant_data["activity"] = {
        "activity_id": "act_456",
        "id": "rest_000789",
        "type": "restaurant",
        "name": "Le Cheval Blanc",
        "start_time": "19:30",
        "end_time": "21:30",
        "description": "Michelin-starred French restaurant with formal dining atmosphere",
        "comments": [
            {
                "user_id": "user789",
                "comment_message": "The food is exceptional but too formal for our family dinner. We want authentic French food but in a more relaxed setting where kids won't disturb others. Maybe a traditional bistro?",
                "trip_place_id": "rest_000789"
            },
            {
                "user_id": "user101",
                "comment_message": "Service was great but €400 for dinner is too much for us. Looking for a more affordable option that still gives us the French experience.",
                "trip_place_id": "rest_000789"
            }
        ]
    }

    # Test Case 3: User wants to change their accommodation
    hotel_data = base_data.copy()
    hotel_data["activity"] = {
        "activity_id": "act_789",
        "id": "hotel_000123",
        "type": "hotel",
        "name": "Four Seasons Hotel George V",
        "start_time": "",
        "end_time": "",
        "description": "Luxury 5-star hotel in the 8th arrondissement",
        "comments": [
            {
                "user_id": "user202",
                "comment_message": "This hotel is too expensive for our 9-day stay. We need a more affordable option but still want to be near the main attractions. Somewhere around €200-250 per night would be better.",
                "trip_place_id": "hotel_000123"
            },
            {
                "user_id": "user303",
                "comment_message": "The room is beautiful but not practical for our family. We need a hotel with a kitchenette and maybe connecting rooms. Also would love a pool or kids' play area.",
                "trip_place_id": "hotel_000123"
            }
        ]
    }

    # Initialize agent
    agent = CommentAgent()

    print("\nTesting Place Recommendation:")
    print("Scenario: Family wants to change from Louvre to a more kid-friendly museum")
    place_result = agent.gen_activity_comment(place_data)
    print(json.dumps(place_result, indent=2))

    print("\nTesting Restaurant Recommendation:")
    print("Scenario: Family seeking more casual, affordable French dining experience")
    restaurant_result = agent.gen_activity_comment(restaurant_data)
    print(json.dumps(restaurant_result, indent=2))

    print("\nTesting Hotel Recommendation:")
    print("Scenario: Family needs more affordable, family-oriented accommodation")
    hotel_result = agent.gen_activity_comment(hotel_data)
    print(json.dumps(hotel_result, indent=2))

if __name__ == "__main__":
    main()

    
