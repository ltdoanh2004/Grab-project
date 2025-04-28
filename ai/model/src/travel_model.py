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
        if not self.current_db or not isinstance(self.current_db, HotelVectorDatabase):
            raise ValueError("Hotel database is not set up. Please call setup_database('hotels') first.")
            
        # Get hotel IDs from vector database
        return self.current_db.get_hotel_ids(query_text, top_k=top_k)
    
    def query_places(self, query_text: str, top_k: int = 5) -> List[str]:
        """
        Query places based on text input and return place IDs
        """
        if not self.current_db or not isinstance(self.current_db, PlaceVectorDatabase):
            raise ValueError("Place database is not set up. Please call setup_database('places') first.")
            
        # Get place IDs from vector database
        return self.current_db.get_place_ids(query_text, top_k=top_k)
    
    def query_fnb(self, query_text: str, top_k: int = 5) -> List[str]:
        """
        Query FnB based on text input and return FnB IDs
        """
        if not self.current_db or not isinstance(self.current_db, FnBVectorDatabase):
            raise ValueError("FnB database is not set up. Please call setup_database('fnb') first.")
            
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
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process user query using function calling and return IDs
        """
        try:
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

2. Then, call the appropriate functions in this order:
   a. First, call setup_database for each type needed (hotels, places, fnb)
   b. Then, call the corresponding query functions with detailed context
   c. For each query, include relevant filters (price range, rating, category, etc.)

3. For each function call:
   - Create a detailed context that captures all relevant information
   - Set appropriate top_k value (default 10 for comprehensive results)
   - Include specific filters when applicable

4. Return results in a structured format with:
   - Function name
   - Type of result (hotels, places, fnb)
   - Arguments used
   - List of IDs

Example context for query_hotels:
"Looking for hotels in Da Nang for a family vacation:
- Budget: medium (2-4 million VND/night)
- Duration: 5 days
- Activities: beach, swimming, family-friendly
- Season: summer
- Travel style: family with kids
- Requirements: pool, kids club, beach access"

Remember to:
- Always call setup_database first
- Use multiple functions when needed
- Include all relevant filters
- Create detailed, specific contexts
- Return top 10 results for each query"""
                },
                {"role": "user", "content": user_query}
            ]
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=self.get_available_functions(),
                function_call="auto"
            )
            
            response_message = response.choices[0].message
            
            # If the model decided to call functions
            if response_message.function_call:
                function_name = response_message.function_call.name
                function_args = eval(response_message.function_call.arguments)
                
                # Handle setup_database separately
                if function_name == "setup_database":
                    result = self.setup_database(**function_args)
                    return {
                        "status": "success",
                        "response": f"Database {function_args['db_type']} setup {'successful' if result else 'failed'}"
                    }
                
                # Initialize results dictionary
                results = {
                    "status": "success",
                    "functions": []
                }
                
                # Handle multiple function calls
                if isinstance(function_name, list):
                    for i, name in enumerate(function_name):
                        args = function_args[i] if isinstance(function_args, list) else function_args
                        
                        if name == "query_hotels":
                            ids = self.query_hotels(**args)
                            type = "hotels"
                        elif name == "query_places":
                            ids = self.query_places(**args)
                            type = "places"
                        elif name == "query_fnb":
                            ids = self.query_fnb(**args)
                            type = "fnb"
                        elif name == "search_by_price_range":
                            ids = self.search_by_price_range(**args)
                            type = "hotels"
                        elif name == "search_by_rating":
                            ids = self.search_by_rating(**args)
                            type = "hotels"
                        elif name == "search_by_category":
                            ids = self.search_by_category(**args)
                            type = "places"
                        elif name == "search_by_location":
                            ids = self.search_by_location(**args)
                            type = "places"
                        elif name == "search_by_menu_item":
                            ids = self.search_by_menu_item(**args)
                            type = "fnb"
                        else:
                            raise ValueError(f"Unknown function: {name}")
                        
                        results["functions"].append({
                            "name": name,
                            "type": type,
                            "args": args,
                            "ids": ids
                        })
                else:
                    # Single function call
                    if function_name == "query_hotels":
                        ids = self.query_hotels(**function_args)
                        type = "hotels"
                    elif function_name == "query_places":
                        ids = self.query_places(**function_args)
                        type = "places"
                    elif function_name == "query_fnb":
                        ids = self.query_fnb(**function_args)
                        type = "fnb"
                    elif function_name == "search_by_price_range":
                        ids = self.search_by_price_range(**function_args)
                        type = "hotels"
                    elif function_name == "search_by_rating":
                        ids = self.search_by_rating(**function_args)
                        type = "hotels"
                    elif function_name == "search_by_category":
                        ids = self.search_by_category(**function_args)
                        type = "places"
                    elif function_name == "search_by_location":
                        ids = self.search_by_location(**function_args)
                        type = "places"
                    elif function_name == "search_by_menu_item":
                        ids = self.search_by_menu_item(**function_args)
                        type = "fnb"
                    else:
                        raise ValueError(f"Unknown function: {function_name}")
                    
                    results["functions"].append({
                        "name": function_name,
                        "type": type,
                        "args": function_args,
                        "ids": ids
                    })
                
                return results
            
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