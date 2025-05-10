import os
from openai import OpenAI
from dotenv import load_dotenv
from ..vector_database import HotelVectorDatabase, PlaceVectorDatabase, FnBVectorDatabase
from ..promts.travel_promt import travel_suggestion_system_prompt
from ..promts.function_promt import query_hotels, query_places, query_fnb, search_by_price_range, search_by_rating, search_by_category, search_by_location, search_by_menu_item
from typing import List, Dict, Any, Optional
from ..utils.logger import setup_logger

# Set up logger for this module
logger = setup_logger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(ENV_PATH)

class TravelModel:
    def __init__(self):
        """
        Initialize the travel model with OpenAI API key
        """
        self.openai_client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
        self.model = "gpt-4o"
        
        logger.info("Setting up all databases...")
        self.hotel_db = HotelVectorDatabase()
        self.place_db = PlaceVectorDatabase()
        self.fnb_db = FnBVectorDatabase()
        
        # Setup all databases during initialization
        self.hotel_db.set_up_pinecone()
        self.place_db.set_up_pinecone()
        self.fnb_db.set_up_pinecone()
        
        self.current_db = None
        logger.info("All databases setup completed")
        
    def setup_database(self, db_type: str) -> bool:
        """
        Setup database for specific type
        """
        try:
            if db_type == "hotels":
                self.current_db = self.hotel_db
            elif db_type == "places":
                self.current_db = self.place_db
            elif db_type == "fnb":
                self.current_db = self.fnb_db
            else:
                raise ValueError(f"Unknown database type: {db_type}")
            return True
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
            return False
            
    def query_hotels(self, query_text: str, top_k: int = 15) -> List[str]:
        """
        Query hotels based on text input and return hotel IDs
        Limited to top 15 results
        """
        self.current_db = self.hotel_db
        top_k = min(top_k, 15)  # Enforce maximum of 15 results
        return self.current_db.get_hotel_ids(query_text, top_k=top_k)
    
    def query_places(self, query_text: str, top_k: int = 40) -> List[str]:
        """
        Query places based on text input and return place IDs
        Limited to top 40 results
        """
        self.current_db = self.place_db
        top_k = min(top_k, 40)  # Enforce maximum of 40 results
        return self.current_db.get_place_ids(query_text, top_k=top_k)
    
    def query_fnb(self, query_text: str, top_k: int = 40) -> List[str]:
        """
        Query FnB based on text input and return FnB IDs
        Limited to top 40 results
        """
        try:
            self.current_db = self.fnb_db
            top_k = min(top_k, 40)  # Enforce maximum of 40 results
            
            # Log the query attempt
            logger.info(f"Attempting to query FnB with text: {query_text}, top_k: {top_k}")
            
            # Get results
            results = self.current_db.get_fnb_ids(query_text, top_k=top_k)
            
            # Log the results
            logger.info(f"FnB query returned {len(results)} results")
            if not results:
                logger.warning("No FnB results found, trying with broader context")
                # Try with broader context if no results
                broader_query = f"restaurant {query_text}"
                results = self.current_db.get_fnb_ids(broader_query, top_k=top_k)
                logger.info(f"Broader FnB query returned {len(results)} results")
            
            return results
        except Exception as e:
            logger.error(f"Error in query_fnb: {e}", exc_info=True)
            return []
    
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
            query_hotels,
            query_places,
            query_fnb,
            search_by_price_range,
            search_by_rating,
            search_by_category,
            search_by_location,
            search_by_menu_item
        ]
    
    def process_query(self, user_query: str) -> List[Dict[str, str]]:
        """
        Process user query using function calling and return formatted recommendations
        compatible with SuggestWithIDAndType
        """
        try:
            logger.info(f"Processing query: {user_query}")
            
            messages = [
                {
                    "role": "system", 
                    "content": travel_suggestion_system_prompt
                },
                {"role": "user", "content": user_query}
            ]
            
            logger.debug("Sending request to OpenAI...")
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=self.get_available_functions(),
                function_call="auto"
            )
            logger.info(f"OpenAI response: {response}")
            
            response_message = response.choices[0].message
            logger.info(f"Model response message: {response_message}")
            
            search_context = user_query
            if response_message.function_call:
                function_name = response_message.function_call.name
                function_args = eval(response_message.function_call.arguments)
                logger.info(f"Function call: {function_name}")
                logger.debug(f"Function arguments: {function_args}")
                
                if "query_text" in function_args:
                    search_context = function_args.get("query_text", user_query)
                    
                # Set appropriate top_k based on function type
                if function_name == "query_hotels":
                    top_k = min(function_args.get("top_k", 15), 15)
                else:
                    top_k = min(function_args.get("top_k", 40), 40)
            else:
                # Default to maximum allowed values
                top_k = 40
                
            logger.info("Querying all databases with context")
            
            formatted_results = []
            
            # Query hotels (max 15 results)
            logger.info(f"Querying hotels with context: {search_context}")
            hotel_ids = self.query_hotels(search_context, top_k=15)
            for hotel_id in hotel_ids:
                formatted_results.append({
                    "name": f"Hotel {hotel_id}",
                    "type": "accommodation",
                    "args": "hotel",
                    "id": hotel_id
                })
            logger.info(f"Added {len(hotel_ids)} hotel recommendations")
            
            # Query places (max 40 results)
            logger.info(f"Querying places with context: {search_context}")
            place_ids = self.query_places(search_context, top_k=40)
            for place_id in place_ids:
                formatted_results.append({
                    "name": f"Place {place_id}",
                    "type": "place", 
                    "args": "activity",
                    "id": place_id
                })
            logger.info(f"place_ids: {place_ids}")
            logger.info(f"Added {len(place_ids)} place recommendations")
            
            # Query restaurants (max 40 results)
            logger.info(f"Querying restaurants with context: {search_context}")
            restaurant_ids = self.query_fnb(search_context, top_k=40)
            
            # If no restaurant results, try with broader context
            if not restaurant_ids:
                logger.warning("No restaurant results found with original context, trying broader search")
                broader_context = f"restaurant {search_context}"
                restaurant_ids = self.query_fnb(broader_context, top_k=40)
            
            for restaurant_id in restaurant_ids:
                formatted_results.append({
                    "name": f"Restaurant {restaurant_id}",
                    "type": "restaurant",
                    "args": "dining",
                    "id": restaurant_id
                })
            logger.info(f"Added {len(restaurant_ids)} restaurant recommendations")
            
            if not formatted_results:
                logger.warning("No recommendations found, using fallback suggestions")
                formatted_results = [
                    {"name": "Luxury Hotel", "type": "accommodation", "args": "luxury", "id": "hotel_000001"},
                    {"name": "City Museum", "type": "place", "args": "cultural", "id": "place_000001"},
                    {"name": "Local Restaurant", "type": "restaurant", "args": "local cuisine", "id": "restaurant_000001"}
                ]
            
            hotel_count = sum(1 for r in formatted_results if r["type"] == "accommodation")
            place_count = sum(1 for r in formatted_results if r["type"] == "place")
            restaurant_count = sum(1 for r in formatted_results if r["type"] == "restaurant")
            
            logger.info(f"Final result distribution: {hotel_count} hotels, {place_count} places, {restaurant_count} restaurants")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in process_query: {e}", exc_info=True)
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