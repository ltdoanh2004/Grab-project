import os
from openai import OpenAI
from dotenv import load_dotenv
from ai.model.src.vector_database.hotel_vector_database import HotelVectorDatabase
from ai.model.src.vector_database.place_vector_database import PlaceVectorDatabase
from ai.model.src.vector_database.fnb_vector_database import FnBVectorDatabase
from ai.model.src.api.backend_api import BackendAPI
from typing import List, Dict, Any, Optional

# Load environment variables
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(ENV_PATH)

class TravellingChatbot:
    def __init__(self):
        self.hotel_db = HotelVectorDatabase()
        self.place_db = PlaceVectorDatabase()
        self.fnb_db = FnBVectorDatabase()
        self.openai_client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
        self.backend_api = BackendAPI()
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
            
    def query_hotels(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query hotels based on text input
        """
        if not self.current_db or not isinstance(self.current_db, HotelVectorDatabase):
            raise ValueError("Hotel database is not set up. Please call setup_database('hotels') first.")
            
        # Get hotel IDs from vector database
        hotel_ids = self.current_db.get_hotel_ids(query_text, top_k=top_k)
        
        # Get detailed hotel information from backend
        result = self.backend_api.get_location_details(hotel_ids, "hotels")
        if result["status"] == "success":
            return result["data"]
        else:
            raise ValueError(f"Error getting hotel details: {result['error']}")
    
    def query_places(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query places based on text input
        """
        if not self.current_db or not isinstance(self.current_db, PlaceVectorDatabase):
            raise ValueError("Place database is not set up. Please call setup_database('places') first.")
            
        # Get place IDs from vector database
        place_ids = self.current_db.get_place_ids(query_text, top_k=top_k)
        
        # Get detailed place information from backend
        result = self.backend_api.get_location_details(place_ids, "places")
        if result["status"] == "success":
            return result["data"]
        else:
            raise ValueError(f"Error getting place details: {result['error']}")
    
    def query_fnb(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query FnB based on text input
        """
        if not self.current_db or not isinstance(self.current_db, FnBVectorDatabase):
            raise ValueError("FnB database is not set up. Please call setup_database('fnb') first.")
            
        # Get FnB IDs from vector database
        fnb_ids = self.current_db.get_fnb_ids(query_text, top_k=top_k)
        
        # Get detailed FnB information from backend
        result = self.backend_api.get_location_details(fnb_ids, "fnb")
        if result["status"] == "success":
            return result["data"]
        else:
            raise ValueError(f"Error getting FnB details: {result['error']}")
    
    def search_by_price_range(self, min_price: float, max_price: float, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search by price range
        """
        if not self.current_db:
            raise ValueError("No database is set up. Please call setup_database first.")
            
        if isinstance(self.current_db, HotelVectorDatabase):
            results = self.current_db.search_by_price_range(min_price, max_price, top_k)
            ids = [result["id"] for result in results["matches"]]
            result_type = "hotels"
        elif isinstance(self.current_db, PlaceVectorDatabase):
            results = self.current_db.search_by_entrance_fee(max_price, top_k)
            ids = [result["id"] for result in results["matches"]]
            result_type = "places"
        elif isinstance(self.current_db, FnBVectorDatabase):
            results = self.current_db.search_by_price_range(f"{min_price}-{max_price}", top_k)
            ids = [result["id"] for result in results["matches"]]
            result_type = "fnb"
        else:
            raise ValueError("Unsupported database type")
            
        # Get detailed information from backend
        result = self.backend_api.get_location_details(ids, result_type)
        if result["status"] == "success":
            return result["data"]
        else:
            raise ValueError(f"Error getting details: {result['error']}")
    
    def search_by_rating(self, min_rating: float, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search by minimum rating
        """
        if not self.current_db:
            raise ValueError("No database is set up. Please call setup_database first.")
            
        results = self.current_db.search_by_rating(min_rating, top_k)
        ids = [result["id"] for result in results["matches"]]
        
        # Determine result type based on current database
        if isinstance(self.current_db, HotelVectorDatabase):
            result_type = "hotels"
        elif isinstance(self.current_db, PlaceVectorDatabase):
            result_type = "places"
        elif isinstance(self.current_db, FnBVectorDatabase):
            result_type = "fnb"
        else:
            raise ValueError("Unsupported database type")
            
        result = self.backend_api.get_location_details(ids, result_type)
        if result["status"] == "success":
            return result["data"]
        else:
            raise ValueError(f"Error getting details: {result['error']}")
    
    def search_by_category(self, category: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search by category
        """
        if not self.current_db:
            raise ValueError("No database is set up. Please call setup_database first.")
            
        if isinstance(self.current_db, PlaceVectorDatabase):
            results = self.current_db.search_by_category(category, top_k)
            ids = [result["id"] for result in results["matches"]]
            result_type = "places"
        elif isinstance(self.current_db, FnBVectorDatabase):
            results = self.current_db.search_by_category(category, top_k)
            ids = [result["id"] for result in results["matches"]]
            result_type = "fnb"
        else:
            raise ValueError("Category search is only supported for places and FnB")
            
        result = self.backend_api.get_location_details(ids, result_type)
        if result["status"] == "success":
            return result["data"]
        else:
            raise ValueError(f"Error getting details: {result['error']}")
    
    def search_by_location(self, location: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search by location
        """
        if not self.current_db or not isinstance(self.current_db, PlaceVectorDatabase):
            raise ValueError("Location search is only supported for places. Please call setup_database('places') first.")
            
        results = self.current_db.search_by_location(location, top_k)
        ids = [result["id"] for result in results["matches"]]
        
        result = self.backend_api.get_location_details(ids, "places")
        if result["status"] == "success":
            return result["data"]
        else:
            raise ValueError(f"Error getting place details: {result['error']}")
    
    def search_by_menu_item(self, item_name: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search FnB by menu item
        """
        if not self.current_db or not isinstance(self.current_db, FnBVectorDatabase):
            raise ValueError("Menu item search is only supported for FnB. Please call setup_database('fnb') first.")
            
        results = self.current_db.search_by_menu_item(item_name, top_k)
        ids = [result["id"] for result in results["matches"]]
        
        result = self.backend_api.get_location_details(ids, "fnb")
        if result["status"] == "success":
            return result["data"]
        else:
            raise ValueError(f"Error getting FnB details: {result['error']}")
    
    def get_available_functions(self) -> List[Dict[str, Any]]:
        """
        Define available functions for the chatbot
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
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process user query using function calling
        """
        try:
            # Initial chat completion to determine which function to call
            messages = [
                {"role": "system", "content": "You are a helpful travel assistant. Use the available functions to help users find hotels, places, and food & beverage options."},
                {"role": "user", "content": user_query}
            ]
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=self.get_available_functions(),
                function_call="auto"
            )
            
            response_message = response.choices[0].message
            
            # If the model decided to call a function
            if response_message.function_call:
                function_name = response_message.function_call.name
                function_args = eval(response_message.function_call.arguments)
                
                # Call the appropriate function
                if function_name == "setup_database":
                    result = self.setup_database(**function_args)
                    return {
                        "status": "success",
                        "response": f"Database {function_args['db_type']} setup {'successful' if result else 'failed'}"
                    }
                elif function_name == "query_hotels":
                    results = self.query_hotels(**function_args)
                elif function_name == "query_places":
                    results = self.query_places(**function_args)
                elif function_name == "query_fnb":
                    results = self.query_fnb(**function_args)
                elif function_name == "search_by_price_range":
                    results = self.search_by_price_range(**function_args)
                elif function_name == "search_by_rating":
                    results = self.search_by_rating(**function_args)
                elif function_name == "search_by_category":
                    results = self.search_by_category(**function_args)
                elif function_name == "search_by_location":
                    results = self.search_by_location(**function_args)
                elif function_name == "search_by_menu_item":
                    results = self.search_by_menu_item(**function_args)
                else:
                    raise ValueError(f"Unknown function: {function_name}")
                
                # Prepare context for final response
                context = f"Based on the following information, please provide a helpful response to the user's query: {user_query}\n\n"
                for item in results:
                    context += f"Name: {item['name']}\n"
                    context += f"Description: {item['description']}\n"
                    if 'price' in item:
                        context += f"Price: {item['price']}\n"
                    if 'rating' in item:
                        context += f"Rating: {item['rating']}\n"
                    if 'categories' in item:
                        context += f"Categories: {item['categories']}\n"
                    if 'location' in item:
                        context += f"Location: {item['location']}\n"
                    if 'menu_items' in item:
                        context += f"Menu Items: {item['menu_items']}\n"
                    context += "\n"
                
                # Get final response from the model
                messages.append(response_message)
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": context
                })
                
                final_response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                
                return {
                    "status": "success",
                    "response": final_response.choices[0].message.content
                }
            
            # If no function was called, return the direct response
            return {
                "status": "success",
                "response": response_message.content
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            } 