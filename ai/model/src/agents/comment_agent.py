from typing import List, Optional
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vector_database import PlaceVectorDatabase, FnBVectorDatabase, HotelVectorDatabase

class CommentAgent:
    def __init__(self):
        self.place_db = None
        self.fnb_db = None
        self.hotel_db = None
        
        self.openai_api_key = os.getenv("OPEN_API_KEY", "")
        self.client = None
        if self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)
        
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
        
        self._init_databases()

    def _init_databases(self):
        """Initialize vector databases as needed"""
        if self.place_db is None:
            self.place_db = PlaceVectorDatabase()
            self.place_db.set_up_pinecone()
        
        if self.fnb_db is None:
            self.fnb_db = FnBVectorDatabase()
            self.fnb_db.set_up_pinecone()
            
        if self.hotel_db is None:
            self.hotel_db = HotelVectorDatabase()
            self.hotel_db.set_up_pinecone()
    
    def _initialize_llm(self):
        """Initialize LLM client if needed"""
        if self.client is None and self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)
        
        if self.client is None:
            raise ValueError("OpenAI client could not be initialized. Please check your API key.")
    
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
        
        return {
            "suggestion_type": suggestion_type,
            "suggestion_ids": self._extract_suggestion_ids(suggestions),
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
            return []
            
        try:
            self._initialize_llm()
            
            system_message = """
            You are a travel recommendation expert analyzing user comments to understand their desired changes.
            Focus on extracting key aspects:
            1. Current Pain Points:
               - What specific issues are they facing?
               - What aspects are they unhappy with?
            
            2. Desired Changes:
               - What specific improvements do they want?
               - What features are they looking for?
            
            3. Constraints:
               - Budget limitations
               - Time constraints
               - Group-specific needs (family, children, etc.)
               - Location preferences
            
            4. Must-Keep Features:
               - What positive aspects should be maintained?
               - What features they still want to keep?

            Return a JSON object with these fields:
            {
                "pain_points": ["list of specific issues"],
                "desired_features": ["list of wanted features"],
                "constraints": ["list of limitations"],
                "retain_features": ["list of features to keep"]
            }
            """
            
            # Prepare comments for analysis
            comment_text = " | ".join([
                comment.get("comment_message", "")
                for comment in comments
                if comment.get("comment_message")
            ])
            
            if not comment_text:
                return []
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Analyze these comments for change requests: {comment_text}"}
                ],
                response_format={"type": "json_object"}
            )
            
            try:
                analysis = json.loads(response.choices[0].message.content)
                return analysis
            except:
                return self._extract_basic_intentions(comments)
                
        except Exception as e:
            print(f"Error analyzing comment intentions: {e}")
            return self._extract_basic_intentions(comments)

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

    def _get_suggestions_by_type(self, data, query, suggestion_type):
        """Get suggestions for a specific type"""
        suggestions = []
        
        try:
            if suggestion_type == "restaurant":
                fnb_ids, fnb_results = self.fnb_db.query(query, top_k=10)
                for match in fnb_results.get("matches", []):
                    suggestions.append({
                        "id": match["id"],
                        "name": match["metadata"].get("name", ""),
                        "type": "restaurant",
                        "score": match["score"]
                    })
                    
            elif suggestion_type == "place":
                place_ids, place_results = self.place_db.query(query, top_k=10)
                for match in place_results.get("matches", []):
                    suggestions.append({
                        "id": match["id"],
                        "name": match["metadata"].get("name", ""),
                        "type": "place",
                        "score": match["score"]
                    })
                    
            elif suggestion_type == "hotel":
                hotel_ids, hotel_results = self.hotel_db.query(query, top_k=10)
                for match in hotel_results.get("matches", []):
                    suggestions.append({
                        "id": match["id"],
                        "name": match["metadata"].get("name", ""),
                        "type": "hotel",
                        "score": match["score"]
                    })
        except Exception as e:
            print(f"Error querying database for {suggestion_type}: {e}")
        
        return sorted(suggestions, key=lambda x: x.get("score", 0), reverse=True)
    
    def _extract_suggestion_ids(self, suggestions):
        """Extract IDs from suggestions and return as a list"""
        return [suggestion["id"] for suggestion in suggestions]

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

    
