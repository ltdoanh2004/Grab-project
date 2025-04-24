import torch 
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import os
import argparse
from tqdm import tqdm
from pinecone import Pinecone

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

    def process_room_type(self, room_type):
        if isinstance(room_type, list):  
            return ', '.join(room_type)
        return room_type

    def get_openai_embeddings(self, text):
        response = self.client.embeddings.create(
            input=text,
            model=self.name_model
        )   
        return response.data[0].embedding

    def prepare_hotel_data(self, data=None):
        if data is None:
            data = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'hotel_processed.csv')
            
        print("Loading and processing hotel data...")
        print(f"Loading data from: {data}")
        self.df = pd.read_csv(data)
        
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
                                Có các loại phòng là {self.process_room_type(row['room_types'])}
                                ''' for _, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Creating contexts")]
        return self.df

    def prepare_hotel_embedding(self, data=None):
        self.df = self.prepare_hotel_data(data)

        print("Generating embeddings...")
        embeddings = []
        for text in tqdm(self.df['context'], desc="Generating embeddings", unit="hotel"):
            embedding = self.get_openai_embeddings(text)
            embeddings.append(embedding)
        
        self.df['context_embedding'] = embeddings

        # Save to the same directory as the input file
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'hotel_processed_embedding.csv')
        print(f"Saving processed data to: {output_path}")
        self.df.to_csv(output_path, index=False)

    def set_up_pinecone(self, index_name = 'hotel-recommendations'):
        if not hasattr(self, 'df') or 'context_embedding' not in self.df.columns:
            raise ValueError("DataFrame not prepared or missing embeddings. Please run prepare_hotel_embedding first.")
            
        self.index_name = index_name
        if index_name not in self.pc.list_indexes().names():
            print(f"Creating new index: {index_name}")
            self.pc.create_index(
                name=index_name,
                dimension=self.dimension,
                metric=self.metric
            )
        
        self.index = self.pc.Index(index_name)
        
        print("Inserting data into Pinecone...")
        vectors_to_upsert = []
        
        for idx, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Preparing vectors"):
            metadata = {
                "id": row["index"],
                "name": row["name"],
                "price": row["price"],
                "rating": row["rating"],
                "description": row["description"]
            }
            
            vectors_to_upsert.append({
                "id": str(row["index"]),
                "values": row["context_embedding"],
                "metadata": metadata
            })
            
            # Upsert in batches of 100
            if len(vectors_to_upsert) >= 100:
                self.index.upsert(vectors=vectors_to_upsert)
                vectors_to_upsert = []
        
        # Upsert remaining vectors
        if vectors_to_upsert:
            self.index.upsert(vectors=vectors_to_upsert)
        
        print(f"Successfully inserted {len(self.df)} vectors into Pinecone index: {index_name}")

    def query(self, query_text, top_k=5, include_metadata=True):
        """
        Query the database for similar hotels based on text input
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
        
        return results
    
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

def main():
    parser = argparse.ArgumentParser(description='Vector Database for Hotel Recommendations')
    parser.add_argument('--prepare-data', action='store_true', help='Prepare and process hotel data')
    parser.add_argument('--setup-pinecone', action='store_true', help='Setup Pinecone database')
    parser.add_argument('--query', type=str, help='Query text to search for similar hotels')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    args = parser.parse_args()

    vector_db = VectorDatabase()
    
    if args.prepare_data:
        vector_db.prepare_hotel_embedding()
    
    if args.setup_pinecone:
        vector_db.set_up_pinecone()
        
    if args.query:
        results = vector_db.query(args.query, top_k=args.top_k)
        for match in results['matches']:
            print(f"Hotel: {match['metadata']['name']}")
            print(f"Price: {match['metadata']['price']}")
            print(f"Rating: {match['metadata']['rating']}")
            print(f"Description: {match['metadata']['description']}")
            print("-" * 50)

if __name__ == "__main__":
    main()