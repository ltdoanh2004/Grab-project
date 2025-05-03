import os
from openai import OpenAI
from dotenv import load_dotenv
from .vector_database import HotelVectorDatabase
from .vector_database import PlaceVectorDatabase
from .vector_database import FnBVectorDatabase
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(ENV_PATH)

class TravelModel:
    def __init__(self):
        self.hotel_db = HotelVectorDatabase()
        self.place_db = PlaceVectorDatabase()
        self.fnb_db = FnBVectorDatabase()
        self.openai_client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
        self.model = "gpt-3.5-turbo"
        self.current_db = None
        
    def setup_database(self, db_type: str) -> bool:
        """
        Setup database for specific type
        """
        try:
            if db_type == "hotels":
                self.hotel_db.set_up_pinecone()
                self.current_db = self.hotel_db
            elif db_type == "places":
                self.place_db.set_up_pinecone()
                self.current_db = self.place_db
            elif db_type == "fnb":
                self.fnb_db.set_up_pinecone()
                self.current_db = self.fnb_db
            else:
                raise ValueError(f"Unknown database type: {db_type}")
            return True
        except Exception as e:
            print(f"Error setting up database: {e}")
            return False
            
    def query_hotels(self, query_text: str, top_k: int = 5) -> List[str]:
        """
        Query hotels based on text input and return hotel IDs
        """
        # Double-check that hotel database is set up
        if not self.current_db or not isinstance(self.current_db, HotelVectorDatabase):
            logger.warning("Hotel database was not set up. Setting up now...")
            self.setup_database("hotels")
            
        # Get hotel IDs from vector database
        return self.current_db.get_hotel_ids(query_text, top_k=top_k)
    
    def query_places(self, query_text: str, top_k: int = 5) -> List[str]:
        """
        Query places based on text input and return place IDs
        """
        # Double-check that places database is set up
        if not self.current_db or not isinstance(self.current_db, PlaceVectorDatabase):
            logger.warning("Places database was not set up. Setting up now...")
            self.setup_database("places")
            
        # Get place IDs from vector database
        return self.current_db.get_place_ids(query_text, top_k=top_k)
    
    def query_fnb(self, query_text: str, top_k: int = 5) -> List[str]:
        """
        Query FnB based on text input and return FnB IDs
        """
        # Double-check that FnB database is set up
        if not self.current_db or not isinstance(self.current_db, FnBVectorDatabase):
            logger.warning("FnB database was not set up. Setting up now...")
            self.setup_database("fnb")
            
        # Get FnB IDs from vector database
        return self.current_db.get_fnb_ids(query_text, top_k=top_k)
    
    def search_by_price_range(self, min_price: float, max_price: float, top_k: int = 5) -> List[str]:
        """
        Search by price range and return IDs
        """
        if not self.current_db:
            raise ValueError("No database is set up. Please call setup_database first.")
            
        if isinstance(self.current_db, HotelVectorDatabase):
            results = self.current_db.search_by_price_range(min_price, max_price, top_k)
        elif isinstance(self.current_db, PlaceVectorDatabase):
            results = self.current_db.search_by_entrance_fee(max_price, top_k)
        elif isinstance(self.current_db, FnBVectorDatabase):
            results = self.current_db.search_by_price_range(f"{min_price}-{max_price}", top_k)
        else:
            raise ValueError("Unsupported database type")
            
        return [result["id"] for result in results["matches"]]
    
    def search_by_rating(self, min_rating: float, top_k: int = 5) -> List[str]:
        """
        Search by minimum rating and return IDs
        """
        if not self.current_db:
            raise ValueError("No database is set up. Please call setup_database first.")
            
        results = self.current_db.search_by_rating(min_rating, top_k)
        return [result["id"] for result in results["matches"]]
    
    def search_by_category(self, category: str, top_k: int = 5) -> List[str]:
        """
        Search by category and return IDs
        """
        if not self.current_db:
            raise ValueError("No database is set up. Please call setup_database first.")
            
        if isinstance(self.current_db, PlaceVectorDatabase):
            results = self.current_db.search_by_category(category, top_k)
        elif isinstance(self.current_db, FnBVectorDatabase):
            results = self.current_db.search_by_category(category, top_k)
        else:
            raise ValueError("Category search is only supported for places and FnB")
            
        return [result["id"] for result in results["matches"]]
    
    def search_by_location(self, location: str, top_k: int = 5) -> List[str]:
        """
        Search by location and return IDs
        """
        if not self.current_db or not isinstance(self.current_db, PlaceVectorDatabase):
            raise ValueError("Location search is only supported for places. Please call setup_database('places') first.")
            
        results = self.current_db.search_by_location(location, top_k)
        return [result["id"] for result in results["matches"]]
    
    def search_by_menu_item(self, item_name: str, top_k: int = 5) -> List[str]:
        """
        Search FnB by menu item and return IDs
        """
        if not self.current_db or not isinstance(self.current_db, FnBVectorDatabase):
            raise ValueError("Menu item search is only supported for FnB. Please call setup_database('fnb') first.")
            
        results = self.current_db.search_by_menu_item(item_name, top_k)
        return [result["id"] for result in results["matches"]]
    
    def get_available_functions(self) -> List[Dict[str, Any]]:
        """
        Define available functions for the model
        """
        return [
            {
                "name": "setup_database",
                "description": "Setup database for specific type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "db_type": {
                            "type": "string",
                            "description": "Type of database (hotels, places, fnb)",
                            "enum": ["hotels", "places", "fnb"]
                        }
                    },
                    "required": ["db_type"]
                }
            },
            {
                "name": "query_hotels",
                "description": "Query hotels based on text input",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_text": {
                            "type": "string",
                            "description": "The query text to search for hotels"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of hotels to return",
                            "default": 5
                        }
                    },
                    "required": ["query_text"]
                }
            },
            {
                "name": "query_places",
                "description": "Query places based on text input",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_text": {
                            "type": "string",
                            "description": "The query text to search for places"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of places to return",
                            "default": 5
                        }
                    },
                    "required": ["query_text"]
                }
            },
            {
                "name": "query_fnb",
                "description": "Query FnB based on text input",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_text": {
                            "type": "string",
                            "description": "The query text to search for FnB"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of FnB to return",
                            "default": 5
                        }
                    },
                    "required": ["query_text"]
                }
            },
            {
                "name": "search_by_price_range",
                "description": "Search within a specific price range",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min_price": {
                            "type": "number",
                            "description": "Minimum price for search"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price for search"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["min_price", "max_price"]
                }
            },
            {
                "name": "search_by_rating",
                "description": "Search with minimum rating",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min_rating": {
                            "type": "number",
                            "description": "Minimum rating for search"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["min_rating"]
                }
            },
            {
                "name": "search_by_category",
                "description": "Search by category",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Category to search for"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["category"]
                }
            },
            {
                "name": "search_by_location",
                "description": "Search places by location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location to search for"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "search_by_menu_item",
                "description": "Search FnB by menu item",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_name": {
                            "type": "string",
                            "description": "Menu item to search for"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["item_name"]
                }
            }
        ]
    
    def process_query(self, user_query: str) -> List[Dict[str, str]]:
        """
        Process user query using function calling and return formatted recommendations
        compatible with SuggestWithIDAndType
        """
        try:
            logger.info(f"Processing query: {user_query}")
            
            # Initial chat completion to determine which functions to call
            messages = [
                {
                    "role": "system", 
                    "content": """You are an expert travel assistant specialized in Vietnam tourism. Your goal is to help users find the best accommodations, activities, and restaurants based on their preferences.

When processing a query:
1. First, analyze the user's request to understand their needs:
   - Type of travel (leisure, business, family, etc.)
   - Budget range
   - Duration of stay
   - Location preferences
   - Activities of interest
   - Travel style (luxury, budget, adventure, etc.)
   - Season of travel

2. Then, call the appropriate query functions with detailed context:
   - query_hotels: For finding accommodations
   - query_places: For finding attractions and activities
   - query_fnb: For finding restaurants and food options

3. For each function call:
   - Create a detailed context that captures all relevant information
   - Set appropriate top_k value (default 10 for comprehensive results)
   - Include specific filters when applicable

Remember to:
- Create detailed, specific contexts for each query
- Return top 10 results for each query"""
                },
                {"role": "user", "content": user_query}
            ]
            
            # Always setup all databases first
            for db_type in ["hotels", "places", "fnb"]:
                logger.info(f"Force setting up database: {db_type}")
                self.setup_database(db_type)
                messages.append({"role": "assistant", "content": f"Database {db_type} has been set up."})
            
            logger.debug("Sending request to OpenAI after forced database setup...")
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=self.get_available_functions(),
                function_call="auto"
            )
            logger.debug(f"OpenAI response: {response}")
            
            response_message = response.choices[0].message
            logger.info(f"Model response message: {response_message}")
            
            # Get the search context from the model response (if any)
            search_context = user_query
            if response_message.function_call:
                function_name = response_message.function_call.name
                function_args = eval(response_message.function_call.arguments)
                logger.info(f"Function call: {function_name}")
                logger.debug(f"Function arguments: {function_args}")
                
                # Extract query_text from function arguments if available
                if "query_text" in function_args:
                    search_context = function_args.get("query_text", user_query)
                    
                # Get top_k parameter if specified
                top_k = function_args.get("top_k", 10)
            else:
                top_k = 10
                
            # Force calling all three query functions with the same context
            logger.info("Force calling all query functions to ensure complete results")
            
            # Results will store all recommendations
            formatted_results = []
            
            # Query hotels
            logger.info(f"Force querying hotels with context: {search_context}")
            hotel_ids = self.query_hotels(search_context, top_k=top_k)
            for hotel_id in hotel_ids:
                formatted_results.append({
                    "name": f"Hotel {hotel_id}",
                    "type": "accommodation",
                    "args": "hotel",
                    "id": hotel_id
                })
            logger.info(f"Added {len(hotel_ids)} hotel recommendations")
            
            # Query places
            logger.info(f"Force querying places with context: {search_context}")
            place_ids = self.query_places(search_context, top_k=top_k)
            for place_id in place_ids:
                formatted_results.append({
                    "name": f"Place {place_id}",
                    "type": "place", 
                    "args": "activity",
                    "id": place_id
                })
            logger.info(f"Added {len(place_ids)} place recommendations")
            
            # Query restaurants
            logger.info(f"Force querying restaurants with context: {search_context}")
            restaurant_ids = self.query_fnb(search_context, top_k=top_k)
            for restaurant_id in restaurant_ids:
                formatted_results.append({
                    "name": f"Restaurant {restaurant_id}",
                    "type": "restaurant",
                    "args": "dining",
                    "id": restaurant_id
                })
            logger.info(f"Added {len(restaurant_ids)} restaurant recommendations")
            
            # If no results, provide fallback recommendations
            if not formatted_results:
                logger.warning("No recommendations found, using fallback suggestions")
                formatted_results = [
                    {"name": "Luxury Hotel", "type": "accommodation", "args": "luxury", "id": "hotel_000001"},
                    {"name": "City Museum", "type": "place", "args": "cultural", "id": "place_000001"},
                    {"name": "Local Restaurant", "type": "restaurant", "args": "local cuisine", "id": "restaurant_000001"}
                ]
            
            logger.info(f"Total recommendations: {len(formatted_results)}")
            return formatted_results[:10]  # Limit to top 10 recommendations
            
        except Exception as e:
            logger.error(f"Error in process_query: {e}", exc_info=True)
            # Return fallback recommendations in case of error
            return [
                {"name": "Luxury Hotel", "type": "accommodation", "args": "luxury", "id": "hotel_000001"},
                {"name": "City Museum", "type": "place", "args": "cultural", "id": "place_000001"},
                {"name": "Local Restaurant", "type": "restaurant", "args": "local cuisine", "id": "restaurant_000001"}
            ]
            
    def _process_function_call(self, function_name: str, args: Dict[str, Any], results: Dict[str, Any]):
        """Helper method to process a function call and update results"""
        try:
            logger.debug(f"Processing function call: {function_name} with args: {args}")
            if function_name == "query_hotels":
                ids = self.query_hotels(**args)
                results["results"]["hotels"]["ids"].extend(ids)
                logger.info(f"Added {len(ids)} hotel IDs")
            elif function_name == "query_places":
                ids = self.query_places(**args)
                results["results"]["places"]["ids"].extend(ids)
                logger.info(f"Added {len(ids)} place IDs")
            elif function_name == "query_fnb":
                ids = self.query_fnb(**args)
                results["results"]["restaurants"]["ids"].extend(ids)
                logger.info(f"Added {len(ids)} restaurant IDs")
            elif function_name == "search_by_price_range":
                ids = self.search_by_price_range(**args)
                results["results"]["hotels"]["ids"].extend(ids)
                logger.info(f"Added {len(ids)} hotel IDs from price range search")
            elif function_name == "search_by_rating":
                ids = self.search_by_rating(**args)
                results["results"]["hotels"]["ids"].extend(ids)
                logger.info(f"Added {len(ids)} hotel IDs from rating search")
            elif function_name == "search_by_category":
                ids = self.search_by_category(**args)
                results["results"]["places"]["ids"].extend(ids)
                logger.info(f"Added {len(ids)} place IDs from category search")
            elif function_name == "search_by_location":
                ids = self.search_by_location(**args)
                results["results"]["places"]["ids"].extend(ids)
                logger.info(f"Added {len(ids)} place IDs from location search")
            elif function_name == "search_by_menu_item":
                ids = self.search_by_menu_item(**args)
                results["results"]["restaurants"]["ids"].extend(ids)
                logger.info(f"Added {len(ids)} restaurant IDs from menu item search")
        except Exception as e:
            logger.error(f"Error processing function {function_name}: {e}", exc_info=True) 