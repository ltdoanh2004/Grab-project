import argparse
from tqdm import tqdm
import os
import pandas as pd
from typing import Dict, Any

from .base_vector_database import BaseVectorDatabase

class PlaceVectorDatabase(BaseVectorDatabase):
    def __init__(self):
        super().__init__(index_name="place-recommendations")

    def prepare_place_embedding(self, data=None):
        """
        Prepare place embeddings with checkpoint support
        """
        # Load data
        if data is None:
            data = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'place_processed.csv')
            
        print("Loading and processing place data...")
        print(f"Loading data from: {data}")
        self.df = pd.read_csv(data)
        
        # Replace NaN values with empty strings for text columns
        text_columns = ['name', 'description', 'categories', 'location', 'opening_hours']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('')
        
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        last_processed = checkpoint["last_processed_index"]
        existing_embeddings = checkpoint["embeddings"]
        
        print(f"Resuming from index {last_processed + 1} out of {len(self.df)} total rows")
        
        print("Processing entrance fees...")
        if 'entrance_fee' in self.df.columns:
            self.df['entrance_fee'] = self.df['entrance_fee'].fillna(0)
            self.df['entrance_fee'] = self.df['entrance_fee'].astype(float)
        
        print("Processing ratings...")
        if 'rating' in self.df.columns:
            self.df['rating'].fillna(self.df['rating'].mean(), inplace=True)
            self.df['rating'] = self.df['rating'].astype(float)

        print("Generating indices...")
        self.df['index'] = ['place_' + str(i).zfill(5) for i in range(1, len(self.df) + 1)]

        print("Creating context strings...")
        self.df['context'] = [f'''
                                Đây là mô tả của địa điểm:
                                {row['description']}
                                Danh mục của nó là {row.get('categories', '')}
                                Địa chỉ của nó là {row.get('location', '')}
                                Giờ mở cửa: {row.get('opening_hours', '')}
                                Phí vào cửa: {row.get('entrance_fee', '0')}
                                Điểm đánh giá của nó là {row.get('rating', '')}
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
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'place_processed_embedding.csv')
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

    def load_data_to_pinecone(self, incremental=True):
        """
        Load and insert data into Pinecone index
        
        Args:
            incremental: If True, only insert new items and update changed ones
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        # Check if index already has data
        index_stats = self.index.describe_index_stats()
        has_data = index_stats['total_vector_count'] > 0
        
        if has_data and not incremental:
            print(f"Index {self.index_name} already contains data. Use incremental=True to add or update data.")
            return True
            
        # Load data from CSV
        self.df = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'place_processed_embedding.csv'))
        text_columns = ['name', 'description', 'categories', 'location', 'opening_hours']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('')
                
        if not hasattr(self, 'df') or 'context_embedding' not in self.df.columns:
            raise ValueError("DataFrame not prepared or missing embeddings. Please run prepare_place_embedding first.")
            
        # Use base class method for incremental updates if requested
        if incremental:
            # Convert string embeddings to lists if needed before passing to incremental method
            return self.load_data_to_pinecone_incremental(df=self.df, id_field="index", batch_size=100)
            
        # Otherwise, continue with original full insertion method
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
                    "categories": row.get("categories", ""),
                    "location": row.get("location", ""),
                    "opening_hours": row.get("opening_hours", ""),
                    "entrance_fee": row.get("entrance_fee", 0),
                    "rating": row.get("rating", 0),
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

    def get_place_by_id(self, place_id):
        """
        Retrieve a specific place by its ID
        """
        return self.get_item_by_id(place_id)
    
    def update_place(self, place_id, new_data):
        """
        Update place information in the database
        """
        def generate_place_context(metadata):
            """Generate context for place embedding"""
            return f'''
                Đây là mô tả của địa điểm:
                {metadata['description']}
                Danh mục của nó là {metadata.get('categories', '')}
                Địa chỉ của nó là {metadata.get('location', '')}
                Giờ mở cửa: {metadata.get('opening_hours', '')}
                Phí vào cửa: {metadata.get('entrance_fee', '0')}
                Điểm đánh giá của nó là {metadata.get('rating', '')}
            '''
        
        # Check if we need to generate new context and embedding
        needs_new_context = any(key in new_data for key in ['description', 'categories', 'location', 'opening_hours', 'entrance_fee', 'rating'])
        
        # Use the base class update_item method with our custom context generator
        return self.update_item(
            place_id, 
            new_data, 
            generate_context_func=generate_place_context if needs_new_context else None
        )
    
    def delete_place(self, place_id):
        """
        Delete place from the database
        """
        return self.delete_item(place_id)
    
    def get_all_places(self, limit=1000):
        """
        Get all places in the database (with pagination)
        """
        return self.get_all_items(limit)
    
    def search_by_category(self, category, top_k=5):
        """
        Search for places by category
        """
        try:
            # Get all places and filter by category
            all_places = self.get_all_places()
            filtered_places = [
                match for match in all_places['matches']
                if category.lower() in match['metadata']['categories'].lower()
            ]
            
            return {'matches': filtered_places[:top_k]}
        except Exception as e:
            print(f"Error searching by category: {e}")
            return None
    
    def search_by_location(self, location, top_k=5):
        """
        Search for places by location
        """
        try:
            # Get all places and filter by location
            all_places = self.get_all_places()
            filtered_places = [
                match for match in all_places['matches']
                if location.lower() in match['metadata']['location'].lower()
            ]
            
            return {'matches': filtered_places[:top_k]}
        except Exception as e:
            print(f"Error searching by location: {e}")
            return None
    
    def search_by_entrance_fee(self, max_fee, top_k=5):
        """
        Search for places with entrance fee less than or equal to max_fee
        """
        try:
            # Get all places and filter by entrance fee
            all_places = self.get_all_places()
            filtered_places = [
                match for match in all_places['matches']
                if float(match['metadata']['entrance_fee']) <= float(max_fee)
            ]
            
            return {'matches': filtered_places[:top_k]}
        except Exception as e:
            print(f"Error searching by entrance fee: {e}")
            return None
    
    def search_by_rating(self, min_rating, top_k=5):
        """
        Search for places with minimum rating
        """
        try:
            # Get all places and filter by rating
            all_places = self.get_all_places()
            filtered_places = [
                match for match in all_places['matches']
                if float(match['metadata']['rating']) >= float(min_rating)
            ]
            
            return {'matches': filtered_places[:top_k]}
        except Exception as e:
            print(f"Error searching by rating: {e}")
            return None

    def get_place_ids(self, query_text, top_k=5):
        """
        Get place IDs from query results
        """
        ids, _ = self.query(query_text, top_k=top_k)
        return ids

def main():
    parser = argparse.ArgumentParser(description='Vector Database for Place Recommendations')
    parser.add_argument('--prepare-data', action='store_true', help='Prepare and process place data')
    parser.add_argument('--setup-pinecone', action='store_true', help='Setup Pinecone database')
    parser.add_argument('--insert-data', action='store_true', help='Insert data into Pinecone')
    parser.add_argument('--incremental', action='store_true', help='Use incremental update for data insertion')
    parser.add_argument('--query', type=str, help='Query text to search for similar places')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    args = parser.parse_args()

    vector_db = PlaceVectorDatabase()
    
    if args.prepare_data:
        vector_db.prepare_place_embedding()
    
    if args.setup_pinecone:
        vector_db.set_up_pinecone()
        if args.insert_data:
            vector_db.load_data_to_pinecone(incremental=args.incremental)
        
    if args.query:
        # Check if Pinecone is set up, if not, set it up first
        if not vector_db.index:
            print("Pinecone index not initialized. Setting up now...")
            if not vector_db.set_up_pinecone():
                print("Failed to setup Pinecone. Please run prepare_place_embedding first.")
                return
            
        place_ids, results = vector_db.query(args.query, top_k=args.top_k)
        print("Place IDs:")
        for place_id in place_ids:
            print(place_id)
        print("\nFull results:")
        for match in results['matches']:
            print(f"Name: {match['metadata']['name']}")
            print(f"Categories: {match['metadata']['categories']}")
            print(f"Location: {match['metadata']['location']}")
            print(f"Opening Hours: {match['metadata']['opening_hours']}")
            print(f"Entrance Fee: {match['metadata']['entrance_fee']}")
            print(f"Rating: {match['metadata']['rating']}")
            print(f"Description: {match['metadata']['description']}")
            print("-" * 50)

if __name__ == "__main__":
    main() 