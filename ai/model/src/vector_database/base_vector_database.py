import torch 
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import os
import json
from tqdm import tqdm
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')

# Load environment variables from the correct path
load_dotenv(ENV_PATH)

# Get API keys after loading .env
OPEN_API_KEY = os.getenv("OPEN_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not OPEN_API_KEY or not PINECONE_API_KEY:
    raise ValueError(f"Please set OPEN_API_KEY and PINECONE_API_KEY in your .env file at {ENV_PATH}")

print(f"Loading environment variables from: {ENV_PATH}")
print(f"OPEN_API_KEY exists: {bool(OPEN_API_KEY)}")
print(f"PINECONE_API_KEY exists: {bool(PINECONE_API_KEY)}")

class BaseVectorDatabase:
    def __init__(self, index_name="default-index"):
        self.index = None
        self.dimension = 1536
        self.metric = "cosine"
        self.index_name = index_name
        self.open_api_key = OPEN_API_KEY
        self.name_model = "text-embedding-3-small"
        self.client = OpenAI(api_key=self.open_api_key)
        self.pinecone_api_key = PINECONE_API_KEY
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.checkpoint_file = os.path.join(SCRIPT_DIR, f'{index_name}_checkpoint.json')
        self.max_tokens = 8000  # Slightly less than 8192 to be safe
        self.df = None

    def truncate_text(self, text: str) -> str:
        """
        Truncate text to fit within token limit
        """
        if len(text) <= self.max_tokens:
            return text
            
        # Simple truncation - you might want to use a more sophisticated method
        return text[:self.max_tokens]

    def get_openai_embeddings(self, text: str) -> List[float]:
        """
        Get embeddings from OpenAI API with error handling
        """
        try:
            # Truncate text if too long
            text = self.truncate_text(text)
            
            response = self.client.embeddings.create(
                input=text,
                model=self.name_model
            )   
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return None

    def load_checkpoint(self) -> Dict[str, Any]:
        """
        Load checkpoint data if exists
        """
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint_data = json.load(f)
                    print(f"Loaded checkpoint from {self.checkpoint_file}")
                    print(f"Last processed index: {checkpoint_data['last_processed_index']}")
                    print(f"Number of saved embeddings: {len(checkpoint_data['embeddings'])}")
                    return checkpoint_data
            except Exception as e:
                print(f"Error loading checkpoint: {e}")
                return {
                    "last_processed_index": -1,
                    "embeddings": {}
                }
        return {
            "last_processed_index": -1,
            "embeddings": {}
        }

    def save_checkpoint(self, checkpoint_data: Dict[str, Any]):
        """
        Save checkpoint data
        """
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f)
            print(f"Saved checkpoint to {self.checkpoint_file}")
        except Exception as e:
            print(f"Error saving checkpoint: {e}")

    def set_up_pinecone(self, index_name=None):
        """
        Set up Pinecone index connection
        
        Args:
            index_name (str): Name of the index
        """
        if index_name:
            self.index_name = index_name
            
        existing_indexes = self.pc.list_indexes()
        
        # Check if index exists
        if self.index_name not in [index.name for index in existing_indexes]:
            print(f"Creating new index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        
        self.index = self.pc.Index(self.index_name)
        print(f"Connected to Pinecone index: {self.index_name}")
        return True

    def query(self, query_text, top_k=5, include_metadata=True):
        """
        Query the database for similar items based on text input
        Returns a tuple of (ids, full_results)
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        # Generate embedding for the query
        query_embedding = self.get_openai_embeddings(query_text)
        
        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=include_metadata
        )
        
        # Extract IDs
        ids = [match['id'] for match in results['matches']]
        
        return ids, results

    def get_item_by_id(self, item_id):
        """
        Retrieve a specific item by its ID
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        try:
            result = self.index.fetch(ids=[str(item_id)])
            return result
        except Exception as e:
            print(f"Error fetching item: {e}")
            return None
    
    def update_item(self, item_id, new_data, generate_context_func=None):
        """
        Update an item's information in the database
        
        Args:
            item_id: The ID of the item to update
            new_data: Dictionary with new data values
            generate_context_func: Function to generate context for embedding (if None, no new embedding is generated)
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        # Get current item data
        current_data = self.get_item_by_id(item_id)
        if not current_data:
            raise ValueError(f"Item with ID {item_id} not found")
            
        # Update metadata
        metadata = current_data['vectors'][str(item_id)]['metadata']
        metadata.update(new_data)
        
        # Generate new embedding if context generation function is provided
        if generate_context_func:
            context = generate_context_func(metadata)
            new_embedding = self.get_openai_embeddings(context)
        else:
            new_embedding = current_data['vectors'][str(item_id)]['values']
        
        # Update in Pinecone
        self.index.upsert(
            vectors=[{
                "id": str(item_id),
                "values": new_embedding,
                "metadata": metadata
            }]
        )
        
        return True
    
    def delete_item(self, item_id):
        """
        Delete an item from the database
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        try:
            self.index.delete(ids=[str(item_id)])
            return True
        except Exception as e:
            print(f"Error deleting item: {e}")
            return False
    
    def get_all_items(self, limit=1000):
        """
        Get all items in the database (with pagination)
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        try:
            result = self.index.query(
                vector=[0] * self.dimension,  # Dummy vector
                top_k=limit,
                include_metadata=True
            )
            return result
        except Exception as e:
            print(f"Error fetching all items: {e}")
            return None 