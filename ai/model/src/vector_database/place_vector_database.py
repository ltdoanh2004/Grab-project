import argparse
from tqdm import tqdm
import os
import sys
import pandas as pd
from typing import Dict, Any

# Add parent directory to path for direct execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .base_vector_database import BaseVectorDatabase
except ImportError:
    # When run directly, use absolute import
    from vector_database.base_vector_database import BaseVectorDatabase

class PlaceVectorDatabase(BaseVectorDatabase):
    def __init__(self):
        super().__init__(index_name="place-recommendations")
        # Override checkpoint file path to be specific for places
        self.checkpoint_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'place_checkpoint.json')

    def prepare_place_embedding(self, data=None, incremental=True):
        """
        Prepare place embeddings with checkpoint support
        
        Args:
            data: Path to place_processed.csv file (default: None)
            incremental: If True, only generate embeddings for new items (default: True)
        """
        # Load data
        if data is None:
            data = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'place_processed.csv')
        
        if not os.path.exists(data):
            print(f"Data file not found at: {data}")
            print("Creating example data file...")
            
            data_dir = os.path.dirname(data)
            if not os.path.exists(data_dir):
                print(f"Creating data directory: {data_dir}")
                os.makedirs(data_dir, exist_ok=True)
                
            example_data = pd.DataFrame({
                'name': ['Lăng Chủ tịch Hồ Chí Minh', 'Văn Miếu Quốc Tử Giám', 'Hồ Gươm'],
                'description': [
                    'Di tích lịch sử quan trọng của Việt Nam.',
                    'Trường đại học đầu tiên của Việt Nam, được xây dựng từ năm 1070.',
                    'Hồ nước nằm ở trung tâm Hà Nội, còn được gọi là Hồ Hoàn Kiếm.'
                ],
                'categories': ['Di tích lịch sử', 'Di tích văn hóa', 'Danh lam thắng cảnh'],
                'location': ['Phường Hàng Bài, Quận Hoàn Kiếm, Hà Nội', 'Phường Văn Miếu, Quận Đống Đa, Hà Nội', 'Quận Hoàn Kiếm, Hà Nội'],
                'opening_hours': ['8:00 - 17:00', '8:00 - 17:30', 'Cả ngày'],
                'entrance_fee': [0, 30000, 0],
                'rating': [4.8, 4.6, 4.7]
            })
            
            example_data.to_csv(data, index=False)
            print(f"Created example data file at: {data}")
            
        print("Loading and processing place data...")
        print(f"Loading data from: {data}")
        raw_df = pd.read_csv(data)
        
        text_columns = ['name', 'address', 'duration', 'price', 'description', 'opening_hours', 'reviews']
        for col in text_columns:
            if col in raw_df.columns:
                raw_df[col] = raw_df[col].fillna('')
        

        
        print("Processing ratings...")
        if 'rating' in raw_df.columns:
            raw_df['rating'].fillna(raw_df['rating'].mean(), inplace=True)
            raw_df['rating'] = raw_df['rating'] * 2
            raw_df['rating'] = raw_df['rating'].astype(float)



        # Try to find existing embeddings file if we're doing incremental processing
        existing_df = None
        rows_to_embed = raw_df
        
        if incremental:
            # Check for existing embedding file
            embedding_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         'data', 'place_processed_embedding.csv')
            
            if os.path.exists(embedding_file):
                print(f"Found existing embedding file: {embedding_file}")
                existing_df = pd.read_csv(embedding_file)
                
                # Use base class method to find missing embeddings
                rows_to_embed, existing_df = self.find_missing_embeddings(
                    new_df=raw_df,
                    existing_df=existing_df,
                    id_field="place_id"
                )
                
                if len(rows_to_embed) == 0:
                    print("No new rows to embed. Using existing embeddings.")
                    self.df = existing_df
                    return
        
        print(f"Creating context strings for {len(rows_to_embed)} items...")
        rows_to_embed['context'] = [f'''
                                Đây là mô tả của địa điểm:
                                {row['description']}
                                Tên của nó là{row.get('name', '')}
                                Địa chỉ của nó là {row.get('address', '')}
                                Tỉnh của nó là {row.get('city', '')}
                                Giờ mở cửa: {row.get('opening_hours', '')}
                                Giá/Phí vào cửa: {row.get('price', '0')}
                                Điểm đánh giá của nó là {row.get('rating', '')}
                                Các thể loại của nó là {row.get('categories', '')}
                                ''' for _, row in tqdm(rows_to_embed.iterrows(), total=len(rows_to_embed), desc="Creating contexts")]

        # Load checkpoint
        checkpoint = self.load_checkpoint()
        last_processed = checkpoint["last_processed_index"]
        existing_embeddings = checkpoint["embeddings"]
        
        print(f"Resuming from index {last_processed + 1} out of {len(rows_to_embed)} total rows")
        
        print("Generating embeddings...")
        embeddings = []
        total_rows = len(rows_to_embed)
        
        # Initialize embeddings list with None values
        embeddings = [None] * total_rows
        
        # Fill in existing embeddings from checkpoint
        for idx, embedding in existing_embeddings.items():
            idx = int(idx)
            if idx < len(embeddings):
                embeddings[idx] = embedding
        
        # Process remaining rows
        for idx in tqdm(range(last_processed + 1, total_rows), desc="Generating embeddings"):
            try:
                # Generate new embedding
                embedding = self.get_openai_embeddings(rows_to_embed.iloc[idx]['context'])
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
        
        rows_to_embed['context_embedding'] = embeddings
        
        # Combine with existing data if doing incremental processing
        final_df = rows_to_embed.copy()
        
        if incremental and existing_df is not None:
            # Create a combined dataframe: new embeddings + existing embeddings
            # Filter out any rows from existing_df that might conflict with new_df by index
            existing_indices = set(rows_to_embed['place_id'].astype(str))
            filtered_existing_df = existing_df[~existing_df['place_id'].astype(str).isin(existing_indices)]
            
            # Concatenate the filtered existing data with the new data
            final_df = pd.concat([filtered_existing_df, rows_to_embed], ignore_index=True)
            print(f"Combined {len(rows_to_embed)} new embeddings with {len(filtered_existing_df)} existing embeddings")

        # Save to the same directory as the input file
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'place_processed_embedding.csv')
        print(f"Saving processed data to: {output_path}")
        
        # Convert embeddings to string representation before saving
        final_df['context_embedding'] = final_df['context_embedding'].apply(
            lambda x: str(x) if x is not None else None
        )
        final_df.to_csv(output_path, index=False)
        
        # Clear checkpoint after successful completion
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
            print("Cleared checkpoint after successful completion")
            
        # Set the dataframe on the instance for further use
        self.df = final_df

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
        
        # Define embedding file path
        embedding_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     'data', 'place_processed_embedding.csv')
            
        # Check if embedding file exists
        if not os.path.exists(embedding_file):
            print(f"Embedding file not found at: {embedding_file}")
            print("Creating embeddings first...")
            
            # Check if data directory exists
            data_dir = os.path.dirname(embedding_file)
            if not os.path.exists(data_dir):
                print(f"Creating data directory: {data_dir}")
                os.makedirs(data_dir, exist_ok=True)
                
            # Create embeddings from raw data
            self.prepare_place_embedding(incremental=False)
            
            if not os.path.exists(embedding_file):
                raise ValueError(f"Failed to create embedding file at {embedding_file}")
            
        # Load data from CSV
        print(f"Loading embeddings from: {embedding_file}")
        self.df = pd.read_csv(embedding_file)
        text_columns = ['name', 'description', 'categories', 'location', 'opening_hours', 'price', 'rating']
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
                    "id": row["place_id"],
                    "name": row["name"],
                    "categories": row.get("categories", ""),
                    "opening_hours": row.get("opening_hours", ""),
                    "price": row.get("price", 0),
                    "city": row.get("city", ""),
                    "rating": row.get("rating", 0),
                    "description": row["description"]
                }
                
                # Ensure embedding is a list
                embedding = row["context_embedding"]
                if embedding is None:
                    continue
                    
                vectors_to_upsert.append({
                    "id": str(row["place_id"]),
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
                Giờ mở cửa: {metadata.get('opening_hours', '')}
                Điểm đánh giá của nó là {metadata.get('rating', '')}
            '''
        
        # Check if we need to generate new context and embedding
        needs_new_context = any(key in new_data for key in ['description', 'categories', 'location', 'opening_hours', 'rating'])
        
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

    def update_metadata_from_csv(self, csv_path: str = None, batch_size: int = 100) -> bool:
        """
        Update metadata for all places from a CSV file
        
        Args:
            csv_path: Path to the CSV file containing updated metadata
                     Default: ../data/place_processed_embedding.csv
            batch_size: Number of items to update in each batch
            
        Returns:
            Boolean indicating success
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized. Please run set_up_pinecone first.")
            
        if csv_path is None:
            csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'data', 'place_processed_embedding.csv')
            
        if not os.path.exists(csv_path):
            raise ValueError(f"CSV file not found at: {csv_path}")
            
        print(f"Loading data from: {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Fill NaN values with appropriate defaults
        df['name'] = df['name'].fillna('')
        df['description'] = df['description'].fillna('')
        df['categories'] = df['categories'].fillna('')
        df['opening_hours'] = df['opening_hours'].fillna('')
        df['price'] = df['price'].fillna(0)
        df['city'] = df['city'].fillna('')
        df['rating'] = df['rating'].fillna(0)
        
        print(f"Found {len(df)} items to update")
        
        # Process in batches
        vectors_to_upsert = []
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Updating metadata"):
            try:
                # Get current item data
                current_data = self.get_item_by_id(row['place_id'])
                if not current_data:
                    print(f"Item with ID {row['place_id']} not found in Pinecone")
                    continue
                    
                # Get current values
                current_values = current_data['vectors'][str(row['place_id'])]['values']
                
                # Create new metadata
                metadata = {
                    "id": row["place_id"],
                    "name": row["name"],
                    "categories": row["categories"],
                    "opening_hours": row["opening_hours"],
                    "price": row["price"],
                    "city": row["city"],
                    "rating": row["rating"],
                    "description": row["description"]
                }
                
                vectors_to_upsert.append({
                    "id": str(row["place_id"]),
                    "values": current_values,
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
        
        print(f"Successfully updated metadata for {len(df)} items")
        return True

def main():
    parser = argparse.ArgumentParser(description='Vector Database for Place Recommendations')
    parser.add_argument('--prepare-data', action='store_true', help='Prepare and process place data')
    parser.add_argument('--no-incremental', action='store_true', help='Reprocess all data even if embeddings exist')
    parser.add_argument('--setup-pinecone', action='store_true', help='Setup Pinecone database')
    parser.add_argument('--insert-data', action='store_true', help='Insert data into Pinecone')
    parser.add_argument('--incremental', action='store_true', help='Use incremental update for data insertion')
    parser.add_argument('--query', type=str, help='Query text to search for similar places')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    parser.add_argument('--update-metadata', action='store_true', help='Update metadata from CSV file')
    args = parser.parse_args()

    vector_db = PlaceVectorDatabase()
    
    if args.prepare_data:
        vector_db.prepare_place_embedding(incremental=not args.no_incremental)
    
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
            print(f"Opening Hours: {match['metadata']['opening_hours']}")
            print(f"Rating: {match['metadata']['rating']}")
            print(f"Description: {match['metadata']['description']}")
            print("-" * 50)
    if args.update_metadata:
        vector_db.set_up_pinecone()
        vector_db.update_metadata_from_csv()
if __name__ == "__main__":
    main() 