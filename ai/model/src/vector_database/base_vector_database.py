import torch 
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import os
import sys
import json
from tqdm import tqdm
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Set, Tuple

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.abspath(__file__)))
print(f"SCRIPT_DIR: {SCRIPT_DIR}")
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

    def check_existing_items(self, id_field="index") -> Set[str]:
        """
        Check which items already exist in the Pinecone index
        
        Args:
            id_field: The DataFrame column containing item IDs
            
        Returns:
            A set of existing item IDs
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        # Get stats to see if index has data
        index_stats = self.index.describe_index_stats()
        
        if index_stats['total_vector_count'] == 0:
            print(f"Index {self.index_name} is empty. No existing items.")
            return set()
            
        # Fetch all existing IDs (up to limit)
        try:
            # We can't directly get all IDs, so we need to query with a dummy vector
            # This is not ideal for large datasets, but works for moderate sizes
            limit = 10000  # Adjust as needed
            results = self.index.query(
                vector=[0] * self.dimension,
                top_k=limit,
                include_metadata=False
            )
            
            existing_ids = set(match['id'] for match in results['matches'])
            print(f"Found {len(existing_ids)} existing items in the index.")
            return existing_ids
            
        except Exception as e:
            print(f"Error fetching existing items: {e}")
            return set()
        
    def load_data_to_pinecone_incremental(self, df=None, id_field="index", batch_size=100):
        """
        Load data into Pinecone index with incremental update support
        
        Args:
            df: DataFrame containing data (if None, uses self.df)
            id_field: Column name containing unique IDs
            batch_size: Size of batches for upsert operations
            
        Returns:
            Boolean indicating success
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        # Use provided DataFrame or instance DataFrame
        dataframe = df if df is not None else self.df
        
        if dataframe is None:
            raise ValueError("No DataFrame provided and no instance DataFrame available.")
            
        if 'context_embedding' not in dataframe.columns:
            raise ValueError("DataFrame is missing 'context_embedding' column.")
            
        # Get existing IDs from Pinecone
        existing_ids = self.check_existing_items()
        
        # Convert string embeddings to lists if needed and handle nan values
        print("Processing embeddings...")
        dataframe['context_embedding'] = dataframe['context_embedding'].apply(
            lambda x: eval(x) if isinstance(x, str) and x != 'None' and x != 'nan' else None
        )
        
        # Count items for insertion and update
        new_items = [str(id) for id in dataframe[id_field].astype(str) if str(id) not in existing_ids]
        update_items = [str(id) for id in dataframe[id_field].astype(str) if str(id) in existing_ids]
        
        print(f"Found {len(new_items)} new items to insert and {len(update_items)} items to update.")
        
        if len(new_items) == 0 and len(update_items) == 0:
            print("No new or updated items to process.")
            return True
            
        # Prepare vectors for upsert
        print("Preparing vectors...")
        vectors_to_upsert = []
        
        for idx, row in tqdm(dataframe.iterrows(), total=len(dataframe), desc="Processing items"):
            try:
                # Skip if the embedding is None or nan
                if pd.isna(row["context_embedding"]) or row["context_embedding"] is None:
                    print(f"Skipping row {idx} due to missing or invalid embedding")
                    continue
                    
                # Create the vector object with metadata
                item_id = str(row[id_field])
                
                # Create metadata dict from all columns except embedding
                metadata = {}
                for col in dataframe.columns:
                    if col != 'context_embedding' and col in row:
                        value = row[col]
                        # Handle different types of NaN values
                        if pd.isna(value):
                            # Convert NaN to appropriate default values based on column type
                            if col in ['price', 'rating']:
                                metadata[col] = 0.0
                            elif col in ['name', 'description', 'location', 'opening_hours', 'categories']:
                                metadata[col] = ""
                            else:
                                metadata[col] = None
                        else:
                            metadata[col] = value
                
                # Ensure embedding is a list and not nan
                embedding = row["context_embedding"]
                if not isinstance(embedding, list) or any(pd.isna(x) for x in embedding):
                    print(f"Skipping row {idx} due to invalid embedding format")
                    continue
                
                vectors_to_upsert.append({
                    "id": item_id,
                    "values": embedding,
                    "metadata": metadata
                })
                
                # Upsert in batches
                if len(vectors_to_upsert) >= batch_size:
                    self.index.upsert(vectors=vectors_to_upsert)
                    vectors_to_upsert = []
                    
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                continue
        
        # Upsert any remaining vectors
        if vectors_to_upsert:
            self.index.upsert(vectors=vectors_to_upsert)
        
        print(f"Successfully processed data into Pinecone index: {self.index_name}")
        return True 

    def find_missing_embeddings(self, new_df, existing_df=None, id_field="index"):
        """
        Compare new dataframe with existing dataframe to find rows that need embeddings
        
        Args:
            new_df: DataFrame with new or updated data
            existing_df: DataFrame with existing embedded data (if None, try to load from file)
            id_field: Column name containing unique IDs
            
        Returns:
            Tuple containing (rows_to_embed, existing_embedded_df)
        """
        # Make sure ID field exists in new dataframe
        if id_field not in new_df.columns:
            raise ValueError(f"ID field '{id_field}' not found in new dataframe")
            
        # If existing dataframe not provided, try to load from file
        if existing_df is None:
            # Try to find existing embedding file in the same directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filename = f"{self.index_name.replace('-', '_')}_processed_embedding.csv"
            embedding_file = os.path.join(base_dir, 'data', filename)
            
            if os.path.exists(embedding_file):
                print(f"Loading existing embeddings from {embedding_file}")
                existing_df = pd.read_csv(embedding_file)
            else:
                print(f"No existing embedding file found at {embedding_file}")
                # If no existing file, all rows need embeddings
                return new_df, None
                
        # Verify existing dataframe has required columns
        if id_field not in existing_df.columns or 'context_embedding' not in existing_df.columns:
            print("Existing dataframe missing required columns")
            return new_df, existing_df
            
        # Get IDs of rows with embeddings
        existing_ids = set(existing_df[id_field].astype(str))
        
        # Find rows in new dataframe that don't have embeddings yet
        new_ids = set(new_df[id_field].astype(str))
        
        # IDs that need embeddings (either new or updated)
        missing_ids = new_ids - existing_ids
        common_ids = new_ids.intersection(existing_ids)
        
        print(f"Found {len(missing_ids)} new items that need embeddings")
        print(f"Found {len(common_ids)} items that already have embeddings")
        
        if len(missing_ids) == 0:
            print("No new items to embed.")
            return pd.DataFrame(), existing_df
            
        # Filter new_df to only include rows that need embeddings
        rows_to_embed = new_df[new_df[id_field].astype(str).isin(missing_ids)].copy()
        
        return rows_to_embed, existing_df 

    def update_metadata(self, item_id: str, new_metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for an existing item without regenerating embeddings
        
        Args:
            item_id: The ID of the item to update
            new_metadata: Dictionary containing new metadata values
            
        Returns:
            Boolean indicating success
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        try:
            # Get current item data
            current_data = self.get_item_by_id(item_id)
            if not current_data:
                raise ValueError(f"Item with ID {item_id} not found")
                
            # Get current metadata and values
            current_metadata = current_data['vectors'][str(item_id)]['metadata']
            current_values = current_data['vectors'][str(item_id)]['values']
            
            # Update metadata with new values
            # Handle NaN values in new_metadata
            processed_metadata = {}
            for key, value in new_metadata.items():
                if pd.isna(value):
                    if key in ['price', 'rating']:
                        processed_metadata[key] = 0.0
                    elif key in ['name', 'description', 'location', 'opening_hours', 'categories']:
                        processed_metadata[key] = ""
                    else:
                        processed_metadata[key] = None
                else:
                    processed_metadata[key] = value
            
            # Merge with existing metadata
            current_metadata.update(processed_metadata)
            
            # Update in Pinecone
            self.index.upsert(
                vectors=[{
                    "id": str(item_id),
                    "values": current_values,  # Keep existing embedding
                    "metadata": current_metadata
                }]
            )
            
            print(f"Successfully updated metadata for item {item_id}")
            return True
            
        except Exception as e:
            print(f"Error updating metadata for item {item_id}: {e}")
            return False 