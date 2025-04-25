import torch 
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import os
import argparse
from tqdm import tqdm
from pinecone import Pinecone, ServerlessSpec
import json
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

class VectorDatabase:
    def __init__(self):
        self.index = None
        self.dimension = 1536
        self.metric = "cosine"
        self.index_name = "hotel-recommendations"
        self.open_api_key = OPEN_API_KEY
        self.name_model = "text-embedding-3-small"
        self.client = OpenAI(api_key=self.open_api_key)
        self.pinecone_api_key = PINECONE_API_KEY
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.checkpoint_file = os.path.join(SCRIPT_DIR, 'checkpoint.json')
        self.max_tokens = 8000  # Slightly less than 8192 to be safe

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

    def prepare_hotel_embedding(self, data=None):
        """
        Prepare hotel embeddings with checkpoint support
        """
        # Load data
        if data is None:
            data = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'hotel_processed.csv')
            
        print("Loading and processing hotel data...")
        print(f"Loading data from: {data}")
        self.df = pd.read_csv(data)
        
        # Replace NaN values with empty strings for text columns
        text_columns = ['name', 'description', 'room_types']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('')
        
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        last_processed = checkpoint["last_processed_index"]
        existing_embeddings = checkpoint["embeddings"]
        
        print(f"Resuming from index {last_processed + 1} out of {len(self.df)} total rows")
        
        print("Processing prices...")
        self.df['price'] = self.df['price'].replace({'VND': '', ',': '', '\xa0': '', r'\.': ''}, regex=True)
        self.df['price'] = self.df['price'].astype(float)

        print("Processing ratings...")
        self.df['rating'].fillna(self.df['rating'].mean(), inplace=True)
        self.df['rating'] = self.df['rating'].astype(float)

        print("Generating indices...")
        self.df['index'] = ['hotel_' + str(i).zfill(5) for i in range(1, len(self.df) + 1)]

        print("Creating context strings...")
        self.df['context'] = [f'''
                                Đây là mô tả của khách sạn:
                                {row['description']}
                                Gía của nó là {row['price']}
                                Điểm đánh giá của nó là {row['rating']}
                                ''' for _, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Creating contexts")]

        print("Generating embeddings...")
        embeddings = []
        total_rows = len(self.df)
        
        # Initialize embeddings list with None values
        embeddings = [None] * total_rows
        
        # Fill in existing embeddings
        for idx, embedding in existing_embeddings.items():
            embeddings[int(idx)] = embedding
        
        # Process remaining rows
        for idx in tqdm(range(last_processed + 1, total_rows), desc="Generating embeddings"):
            try:
                # Generate new embedding
                embedding = self.get_openai_embeddings(self.df.iloc[idx]['context'])
                embeddings[idx] = embedding
                
                # Update checkpoint every 10 rows
                if idx % 10 == 0:
                    checkpoint["last_processed_index"] = idx
                    checkpoint["embeddings"][str(idx)] = embedding
                    self.save_checkpoint(checkpoint)
                    print(f"Saved checkpoint at index {idx}")
                    
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                # Save checkpoint on error
                checkpoint["last_processed_index"] = idx - 1
                self.save_checkpoint(checkpoint)
                print(f"Saved checkpoint after error at index {idx - 1}")
                raise e
        
        self.df['context_embedding'] = embeddings

        # Save to the same directory as the input file
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'hotel_processed_embedding.csv')
        print(f"Saving processed data to: {output_path}")
        
        # Convert embeddings to string representation before saving
        self.df['context_embedding'] = self.df['context_embedding'].apply(
            lambda x: str(x) if x is not None else None
        )
        self.df.to_csv(output_path, index=False)
        
        # Clear checkpoint after successful completion
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
            print("Cleared checkpoint after successful completion")

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

    def load_data_to_pinecone(self):
        """
        Load and insert data into Pinecone index
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        # Check if index already has data
        index_stats = self.index.describe_index_stats()
        has_data = index_stats['total_vector_count'] > 0
        
        if has_data:
            print(f"Index {self.index_name} already contains data. Skipping data insertion.")
            return True
            
        # Load data from CSV
        self.df = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'hotel_processed_embedding.csv'))
        text_columns = ['name', 'description', 'room_types']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('')
                
        if not hasattr(self, 'df') or 'context_embedding' not in self.df.columns:
            raise ValueError("DataFrame not prepared or missing embeddings. Please run prepare_hotel_embedding first.")
            
        # Convert string embeddings to lists
        print("Converting embeddings to lists...")
        self.df['context_embedding'] = self.df['context_embedding'].apply(
            lambda x: eval(x) if isinstance(x, str) else x
        )
            
        print("Inserting data into Pinecone...")
        vectors_to_upsert = []
        
        for idx, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Preparing vectors"):
            try:
                metadata = {
                    "id": row["index"],
                    "name": row["name"],
                    "price": row["price"],
                    "rating": row["rating"],
                    "description": row["description"]
                }
                
                # Ensure embedding is a list
                embedding = row["context_embedding"]
                if embedding is None:
                    continue
                    
                vectors_to_upsert.append({
                    "id": str(row["index"]),
                    "values": embedding,
                    "metadata": metadata
                })
                
                # Upsert in batches of 100
                if len(vectors_to_upsert) >= 100:
                    self.index.upsert(vectors=vectors_to_upsert)
                    vectors_to_upsert = []
                    
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                continue
        
        # Upsert remaining vectors
        if vectors_to_upsert:
            self.index.upsert(vectors=vectors_to_upsert)
        
        print(f"Successfully inserted {len(self.df)} vectors into Pinecone index: {self.index_name}")
        return True

    def query(self, query_text, top_k=5, include_metadata=True):
        """
        Query the database for similar hotels based on text input
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

    def get_hotel_by_id(self, hotel_id):
        """
        Retrieve a specific hotel by its ID
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        try:
            result = self.index.fetch(ids=[str(hotel_id)])
            return result
        except Exception as e:
            print(f"Error fetching hotel: {e}")
            return None
    
    def update_hotel(self, hotel_id, new_data):
        """
        Update a hotel's information in the database
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        # Get current hotel data
        current_data = self.get_hotel_by_id(hotel_id)
        if not current_data:
            raise ValueError(f"Hotel with ID {hotel_id} not found")
            
        # Update metadata
        metadata = current_data['vectors'][str(hotel_id)]['metadata']
        metadata.update(new_data)
        
        # Generate new context and embedding if description or other key fields changed
        if any(key in new_data for key in ['description', 'price', 'rating', 'room_types']):
            context = f'''
                Đây là mô tả của khách sạn:
                {metadata['description']}
                Gía của nó là {metadata['price']}
                Điểm đánh giá của nó là {metadata['rating']}
                Có các loại phòng là {self.process_room_type(metadata.get('room_types', ''))}
            '''
            new_embedding = self.get_openai_embeddings(context)
        else:
            new_embedding = current_data['vectors'][str(hotel_id)]['values']
        
        # Update in Pinecone
        self.index.upsert(
            vectors=[{
                "id": str(hotel_id),
                "values": new_embedding,
                "metadata": metadata
            }]
        )
        
        return True
    
    def delete_hotel(self, hotel_id):
        """
        Delete a hotel from the database
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        try:
            self.index.delete(ids=[str(hotel_id)])
            return True
        except Exception as e:
            print(f"Error deleting hotel: {e}")
            return False
    
    def get_all_hotels(self, limit=1000):
        """
        Get all hotels in the database (with pagination)
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
            print(f"Error fetching all hotels: {e}")
            return None
    
    def search_by_price_range(self, min_price, max_price, top_k=5):
        """
        Search for hotels within a specific price range
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
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
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        try:
            # Get all hotels and filter by rating
            all_hotels = self.get_all_hotels()
            filtered_hotels = [
                match for match in all_hotels['matches']
                if match['metadata']['rating'] >= min_rating
            ]
            
            return {'matches': filtered_hotels[:top_k]}
        except Exception as e:
            print(f"Error searching by rating: {e}")
            return None

    def get_hotel_ids(self, query_text, top_k=5):
        """
        Get hotel IDs from query results
        """
        results = self.query(query_text, top_k=top_k)
        return [match['id'] for match in results['matches']]

def main():
    parser = argparse.ArgumentParser(description='Vector Database for Hotel Recommendations')
    parser.add_argument('--prepare-data', action='store_true', help='Prepare and process hotel data')
    parser.add_argument('--setup-pinecone', action='store_true', help='Setup Pinecone database')
    parser.add_argument('--insert-data', action='store_true', help='Insert data into Pinecone (only works with --setup-pinecone)')
    parser.add_argument('--query', type=str, help='Query text to search for similar hotels')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    args = parser.parse_args()

    vector_db = VectorDatabase()
    
    if args.prepare_data:
        vector_db.prepare_hotel_embedding()
    
    if args.setup_pinecone:
        vector_db.set_up_pinecone(insert_data=args.insert_data)
        
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