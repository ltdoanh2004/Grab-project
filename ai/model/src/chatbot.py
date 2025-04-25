import os
from openai import OpenAI
from dotenv import load_dotenv
from vector_database import VectorDatabase
from backend_api import BackendAPI
from typing import List, Dict, Any, Optional

# Load environment variables
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(ENV_PATH)

class TravellingChatbot:
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.openai_client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
        self.backend_api = BackendAPI()
        self.model = "gpt-3.5-turbo"
        self.current_index = None
        
    def setup_index(self, index_name: str, data_type: str = "hotels") -> bool:
        """
        Setup index for specific data type
        """
        try:
            self.vector_db.set_up_pinecone(index_name)
            self.current_index = index_name
            return True
        except Exception as e:
            print(f"Error setting up index: {e}")
            return False
            
    def query_hotels(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query hotels based on text input
        """
        if not self.current_index:
            raise ValueError("No index is set up. Please call setup_index first.")
            
        # Get hotel IDs from vector database
        hotel_ids = self.vector_db.get_hotel_ids(query_text, top_k=top_k)
        
        # Get detailed hotel information from backend
        result = self.backend_api.get_location_details(hotel_ids, "hotels")
        if result["status"] == "success":
            return result["data"]
        else:
            raise ValueError(f"Error getting hotel details: {result['error']}")
    
    def search_by_price_range(self, min_price: float, max_price: float, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search hotels by price range
        """
        if not self.current_index:
            raise ValueError("No index is set up. Please call setup_index first.")
            
        hotels = self.vector_db.search_by_price_range(min_price, max_price, top_k)
        hotel_ids = [hotel["id"] for hotel in hotels["matches"]]
        
        # Get detailed hotel information from backend
        result = self.backend_api.get_location_details(hotel_ids, "hotels")
        if result["status"] == "success":
            return result["data"]
        else:
            raise ValueError(f"Error getting hotel details: {result['error']}")
    
    def search_by_rating(self, min_rating: float, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search hotels by minimum rating
        """
        if not self.current_index:
            raise ValueError("No index is set up. Please call setup_index first.")
            
        hotels = self.vector_db.search_by_rating(min_rating, top_k)
        hotel_ids = [hotel["id"] for hotel in hotels["matches"]]
        
        result = self.backend_api.get_location_details(hotel_ids, "hotels")
        if result["status"] == "success":
            return result["data"]
        else:
            raise ValueError(f"Error getting hotel details: {result['error']}")
    
    def get_available_functions(self) -> List[Dict[str, Any]]:
        """
        Define available functions for the chatbot
        """
        return [
            {
                "name": "setup_index",
                "description": "Setup index for specific data type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "index_name": {
                            "type": "string",
                            "description": "Name of the index to setup"
                        },
                        "data_type": {
                            "type": "string",
                            "description": "Type of data (e.g., hotels, attractions, restaurants)",
                            "default": "hotels"
                        }
                    },
                    "required": ["index_name"]
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
                "name": "search_by_price_range",
                "description": "Search hotels within a specific price range",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min_price": {
                            "type": "number",
                            "description": "Minimum price for hotel search"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price for hotel search"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of hotels to return",
                            "default": 5
                        }
                    },
                    "required": ["min_price", "max_price"]
                }
            },
            {
                "name": "search_by_rating",
                "description": "Search hotels with minimum rating",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min_rating": {
                            "type": "number",
                            "description": "Minimum rating for hotel search"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of hotels to return",
                            "default": 5
                        }
                    },
                    "required": ["min_rating"]
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
                {"role": "system", "content": "You are a helpful travel assistant. Use the available functions to help users find hotels and other travel information."},
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
                if function_name == "setup_index":
                    result = self.setup_index(**function_args)
                    return {
                        "status": "success",
                        "response": f"Index {function_args['index_name']} setup {'successful' if result else 'failed'}"
                    }
                elif function_name == "query_hotels":
                    hotels = self.query_hotels(**function_args)
                elif function_name == "search_by_price_range":
                    hotels = self.search_by_price_range(**function_args)
                elif function_name == "search_by_rating":
                    hotels = self.search_by_rating(**function_args)
                else:
                    raise ValueError(f"Unknown function: {function_name}")
                
                # Prepare context for final response
                context = f"Based on the following hotel information, please provide a helpful response to the user's query: {user_query}\n\n"
                for hotel in hotels:
                    context += f"Hotel: {hotel['name']}\n"
                    context += f"Description: {hotel['description']}\n"
                    context += f"Price: {hotel['price']}\n"
                    context += f"Rating: {hotel['rating']}\n\n"
                
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