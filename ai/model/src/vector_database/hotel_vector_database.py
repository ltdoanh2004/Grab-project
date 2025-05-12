import torch 
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import os
import sys
import argparse
from tqdm import tqdm
from pinecone import Pinecone, ServerlessSpec
import json
from typing import List, Dict, Any
import ast  # Add ast import
import numpy as np  # Add numpy import

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .base_vector_database import BaseVectorDatabase
except ImportError:
    from vector_database.base_vector_database import BaseVectorDatabase

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

class HotelVectorDatabase(BaseVectorDatabase):
    def __init__(self):
        super().__init__(index_name="hotel-recommendations")
        self.dimension = 1536
        self.metric = "cosine"
        self.name_model = "text-embedding-3-small"
        self.client = OpenAI(api_key=OPEN_API_KEY)
        self.pinecone_api_key = PINECONE_API_KEY
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.checkpoint_file = os.path.join(SCRIPT_DIR, 'hotel_checkpoint.json')
        self.max_tokens = 8000  

    def process_room_type(self, room_type):
        if isinstance(room_type, list):  
            return ', '.join(room_type)
        return room_type

    def truncate_text(self, text: str) -> str:
        """
        Truncate text to fit within token limit
        """
        if len(text) <= self.max_tokens:
            return text
            
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

    def format_hotel_id(self, idx):
        """Format hotel ID with leading zeros (e.g., hotel_000001)"""
        return f"hotel_{str(idx).zfill(6)}"

    def prepare_hotel_embedding(self, data=None, incremental=True):
        """
        Prepare hotel embeddings with checkpoint support
        
        Args:
            data: Path to hotel_processed.csv file (default: None)
            incremental: If True, only generate embeddings for new items (default: True)
        """
        # Load data
        if data is None:
            data = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'hotel_processed.csv')
            
        # Check if data file exists    
        if not os.path.exists(data):
            print(f"Data file not found at: {data}")
            print("Please provide a valid data file path")
            return
            
        print("Loading and processing hotel data...")
        print(f"Loading data from: {data}")
        raw_df = pd.read_csv(data)
        
        # Format hotel IDs if they don't exist or are not in the correct format
        if 'hotel_id' not in raw_df.columns:
            raw_df['hotel_id'] = [self.format_hotel_id(i) for i in range(len(raw_df))]
        else:
            # Check if IDs are in correct format, if not, reformat them
            def ensure_format(hotel_id):
                if isinstance(hotel_id, str) and hotel_id.startswith('hotel_') and len(hotel_id) == 12:
                    return hotel_id
                try:
                    num = int(str(hotel_id).replace('hotel_', ''))
                    return self.format_hotel_id(num)
                except:
                    return self.format_hotel_id(0)
            
            raw_df['hotel_id'] = raw_df['hotel_id'].apply(ensure_format)
        
        # Replace NaN values with empty strings for text columns
        text_columns = ['name', 'description', 'room_types', 'location', 'elderly_friendly']
        for col in text_columns:
            if col in raw_df.columns:
                raw_df[col] = raw_df[col].fillna('')
        
        print("Processing prices...")
        raw_df['price'] = raw_df['price'].replace({'VND': '', ',': '', '\xa0': '', r'\.': ''}, regex=True)
        raw_df['price'] = pd.to_numeric(raw_df['price'], errors='coerce')
        raw_df['price'] = raw_df['price'].fillna(0)

        print("Processing ratings...")
        raw_df['rating'] = pd.to_numeric(raw_df['rating'], errors='coerce')
        raw_df['rating'] = raw_df['rating'].fillna(raw_df['rating'].mean())
        
        existing_df = None
        rows_to_embed = raw_df
        
        if incremental:
            # Check for existing embedding file
            embedding_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         'data', 'hotel_processed_embedding.csv')
            
            if os.path.exists(embedding_file):
                print(f"Found existing embedding file: {embedding_file}")
                existing_df = pd.read_csv(embedding_file)
                
                # Ensure existing IDs are in correct format
                existing_df['hotel_id'] = existing_df['hotel_id'].apply(ensure_format)
                
                # Use base class method to find missing embeddings
                rows_to_embed, existing_df = self.find_missing_embeddings(
                    new_df=raw_df,
                    existing_df=existing_df,
                    id_field="hotel_id"
                )
                
                if len(rows_to_embed) == 0:
                    print("No new rows to embed. Using existing embeddings.")
                    self.df = existing_df
                    return
        
        print(f"Creating context strings for {len(rows_to_embed)} items...")
        rows_to_embed['context'] = [f'''
                                Thông tin chi tiết về khách sạn:
                                • Tên khách sạn: {row['name']}
                                • Mô tả: {row['description']}
                                • Giá: {row['price']} VND
                                • Đánh giá: {row['rating']} sao
                                • Các loại phòng: {self.process_room_type(row.get('room_types', ''))}
                                • Thân thiện với người cao tuổi/khuyết tật: {"Có" if row.get('elderly_friendly') else "Không"}
                                • Địa điểm/Thành phố: {row.get('location', '')}
                                ''' for _, row in tqdm(rows_to_embed.iterrows(), total=len(rows_to_embed), desc="Creating contexts")]

        checkpoint = self.load_checkpoint()
        last_processed = checkpoint["last_processed_index"]
        existing_embeddings = checkpoint["embeddings"]
        
        print(f"Resuming from index {last_processed + 1} out of {len(rows_to_embed)} total rows")
        
        print("Generating embeddings...")
        embeddings = []
        total_rows = len(rows_to_embed)
        
        embeddings = [None] * total_rows
        
        for idx, embedding in existing_embeddings.items():
            idx = int(idx)
            if idx < len(embeddings):
                embeddings[idx] = embedding
        
        for idx in tqdm(range(last_processed + 1, total_rows), desc="Generating embeddings"):
            try:
                embedding = self.get_openai_embeddings(rows_to_embed.iloc[idx]['context'])
                embeddings[idx] = embedding
                
                if idx % 10 == 0:
                    checkpoint["last_processed_index"] = idx
                    checkpoint["embeddings"][str(idx)] = embedding
                    self.save_checkpoint(checkpoint)
                    print(f"Saved checkpoint at index {idx}")
                    
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                checkpoint["last_processed_index"] = idx - 1
                self.save_checkpoint(checkpoint)
                print(f"Saved checkpoint after error at index {idx - 1}")
                raise e
        
        rows_to_embed['context_embedding'] = embeddings
        
        final_df = rows_to_embed.copy()
        
        if incremental and existing_df is not None:
            existing_indices = set(rows_to_embed['hotel_id'].astype(str))
            filtered_existing_df = existing_df[~existing_df['hotel_id'].astype(str).isin(existing_indices)]
            
            final_df = pd.concat([filtered_existing_df, rows_to_embed], ignore_index=True)
            print(f"Combined {len(rows_to_embed)} new embeddings with {len(filtered_existing_df)} existing embeddings")

        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'hotel_processed_embedding.csv')
        print(f"Saving processed data to: {output_path}")
        
        final_df['context_embedding'] = final_df['context_embedding'].apply(
            lambda x: str(x) if x is not None else None
        )
        final_df.to_csv(output_path, index=False)
        
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
            print("Cleared checkpoint after successful completion")
            
        self.df = final_df

    def set_up_pinecone(self, index_name = 'hotel-recommendations'):
        """
        Set up Pinecone index connection
        
        Args:
            index_name (str): Name of the index
        """
        self.index_name = index_name
        existing_indexes = self.pc.list_indexes()
        
        # Check if index exists
        if index_name not in [index.name for index in existing_indexes]:
            print(f"Creating new index: {index_name}")
            self.pc.create_index(
                name=index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        
        self.index = self.pc.Index(index_name)
        print(f"Connected to Pinecone index: {index_name}")
        return True

    def load_data_to_pinecone(self, incremental=True):
        """
        Load and insert data into Pinecone index
        
        Args:
            incremental: If True, only insert new items and update changed ones
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        index_stats = self.index.describe_index_stats()
        has_data = index_stats['total_vector_count'] > 0
        
        if has_data and not incremental:
            print(f"Index {self.index_name} already contains data. Use incremental=True to add or update data.")
            return True
            
        embedding_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     'data', 'hotel_processed_embedding.csv')
            
        if not os.path.exists(embedding_file):
            print(f"Embedding file not found at: {embedding_file}")
            print("Creating embeddings first...")
            
            data_dir = os.path.dirname(embedding_file)
            if not os.path.exists(data_dir):
                print(f"Creating data directory: {data_dir}")
                os.makedirs(data_dir, exist_ok=True)
                
            self.prepare_hotel_embedding(incremental=False)
            
            if not os.path.exists(embedding_file):
                raise ValueError(f"Failed to create embedding file at {embedding_file}")
        
        print(f"Loading embeddings from: {embedding_file}")
        self.df = pd.read_csv(embedding_file)
        
        text_columns = ['name', 'description', 'room_types', 'location', 'elderly_friendly']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('')
                
        if not hasattr(self, 'df') or 'context_embedding' not in self.df.columns:
            raise ValueError("DataFrame not prepared or missing embeddings. Please run prepare_hotel_embedding first.")
            
        if incremental:
            return self.load_data_to_pinecone_incremental(df=self.df, id_field="hotel_id", batch_size=100)
            
        print("Converting embeddings to lists...")
        def safe_eval_embedding(x):
            if x is None:
                return None
            if not isinstance(x, str):
                return x
            try:
                if x.strip().startswith('[') and x.strip().endswith(']'):
                    return eval(x)
                else:
                    print(f"Warning: Embedding string doesn't look like a list: {x[:50]}...")
                    return None
            except Exception as e:
                print(f"Error evaluating embedding string: {e}")
                return None
                
        self.df['context_embedding'] = self.df['context_embedding'].apply(safe_eval_embedding)
            
        print("Inserting data into Pinecone...")
        vectors_to_upsert = []
        
        for idx, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Preparing vectors"):
            try:
                metadata = {
                    "id": str(row["hotel_id"]),
                    "name": str(row["name"]),
                    "price": float(row["price"]) if pd.notna(row["price"]) else 0.0,
                    "rating": float(row["rating"]) if pd.notna(row["rating"]) else 0.0,
                    "description": str(row["description"]),
                    "city": str(row["location"]),
                    "elderly_friendly": bool(row.get("elderly_friendly", False)),
                    "room_types": str(row.get("room_types", ""))
                }
                
                embedding = row["context_embedding"]
                if embedding is None:
                    continue
                    
                if isinstance(embedding, (int, float)):
                    print(f"Warning: Row {idx} has a non-iterable embedding (type: {type(embedding)}). Skipping.")
                    continue
                
                if not isinstance(embedding, list):
                    try:
                        embedding = list(embedding)
                    except Exception as e:
                        print(f"Error converting embedding to list for row {idx}: {e}")
                        continue

                vectors_to_upsert.append({
                    "id": str(row["hotel_id"]),
                    "values": embedding,
                    "metadata": metadata
                })
                
                if len(vectors_to_upsert) >= 100:
                    self.index.upsert(vectors=vectors_to_upsert)
                    vectors_to_upsert = []
                    
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                continue
        
        if vectors_to_upsert:
            self.index.upsert(vectors=vectors_to_upsert)
        
        print(f"Successfully inserted {len(self.df)} vectors into Pinecone index: {self.index_name}")
        return True

    def query(self, query_text, filter = None, top_k=5, include_metadata=True):
        """
        Query the database for similar hotels based on text input
        Returns a tuple of (ids, full_results)
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        query_embedding = self.get_openai_embeddings(query_text)
        if filter is None:
            filter = {}
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=include_metadata,
            filter = filter
        )
        
        # Extract IDs
        ids = [match['id'] for match in results['matches']]
        
        return ids, results

    def get_hotel_by_id(self, hotel_id):
        """
        Retrieve a specific hotel by its ID
        """
        return self.get_item_by_id(hotel_id)
    
    def update_hotel(self, hotel_id, new_data):
        """
        Update a hotel's information in the database
        """
        def generate_hotel_context(metadata):
            """Generate context for hotel embedding"""
            return f'''
                Đây là mô tả của khách sạn:
                {metadata['description']}
                Gía của nó là {metadata['price']}
                Điểm đánh giá của nó là {metadata['rating']}
                Có các loại phòng là {self.process_room_type(metadata.get('room_types', ''))}
            '''
        
        needs_new_context = any(key in new_data for key in ['description', 'price', 'rating', 'room_types'])
        
        return self.update_item(
            hotel_id, 
            new_data, 
            generate_context_func=generate_hotel_context if needs_new_context else None
        )
    
    def delete_hotel(self, hotel_id):
        """
        Delete a hotel from the database
        """
        return self.delete_item(hotel_id)
    
    def get_all_hotels(self, limit=1000):
        """
        Get all hotels in the database (with pagination)
        """
        return self.get_all_items(limit)
    
    def search_by_price_range(self, min_price, max_price, top_k=5):
        """
        Search for hotels within a specific price range
        """
        try:
            # Get all hotels and filter by price range
            all_hotels = self.get_all_hotels()
            filtered_hotels = [
                match for match in all_hotels['matches']
                if min_price <= match['metadata']['price'] <= max_price
            ]
            
            return {'matches': filtered_hotels[:top_k]}
        except Exception as e:
            print(f"Error searching by price range: {e}")
            return None
    
    def search_by_rating(self, min_rating, top_k=5):
        """
        Search for hotels with minimum rating
        """
        try:
            all_hotels = self.get_all_hotels()
            filtered_hotels = [
                match for match in all_hotels['matches']
                if match['metadata']['rating'] >= min_rating
            ]
            
            return {'matches': filtered_hotels[:top_k]}
        except Exception as e:
            print(f"Error searching by rating: {e}")
            return None

    def get_hotel_ids(self, query_text, filter=None, top_k=5):
        """
        Get hotel IDs from query results
        """
        if filter is None:
            filter = {}
        ids, _ = self.query(query_text, filter=filter, top_k=top_k)
        return ids

def main():
    parser = argparse.ArgumentParser(description='Vector Database for Hotel Recommendations')
    parser.add_argument('--prepare-data', action='store_true', help='Prepare and process hotel data')
    parser.add_argument('--no-incremental', action='store_true', help='Reprocess all data even if embeddings exist')
    parser.add_argument('--setup-pinecone', action='store_true', help='Setup Pinecone database')
    parser.add_argument('--insert-data', action='store_true', help='Insert data into Pinecone')
    parser.add_argument('--incremental', action='store_true', help='Use incremental update for data insertion')
    parser.add_argument('--query', type=str, help='Query text to search for similar hotels')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    args = parser.parse_args()

    vector_db = HotelVectorDatabase()
    
    if args.prepare_data:
        vector_db.prepare_hotel_embedding(incremental=not args.no_incremental)
    
    if args.setup_pinecone:
        vector_db.set_up_pinecone()
        if args.insert_data:
            vector_db.load_data_to_pinecone(incremental=args.incremental)
        
    if args.query:
        # Check if Pinecone is set up, if not, set it up first
        if not vector_db.index:
            print("Pinecone index not initialized. Setting up now...")
            if not vector_db.set_up_pinecone():
                print("Failed to setup Pinecone. Please run prepare_hotel_embedding first.")
                return
            
        hotel_ids, results = vector_db.query(args.query, top_k=args.top_k)
        print("Hotel IDs:")
        for hotel_id in hotel_ids:
            print(hotel_id)
        print("\nFull results:")
        for match in results['matches']:
            print(f"Hotel: {match['metadata']['name']}")
            print(f"Price: {match['metadata']['price']}")
            print(f"Rating: {match['metadata']['rating']}")
            print(f"Description: {match['metadata']['description']}")
            print("-" * 50)

if __name__ == "__main__":
    main()