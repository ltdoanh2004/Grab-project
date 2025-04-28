import argparse
from tqdm import tqdm
import os
import sys
import pandas as pd
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .base_vector_database import BaseVectorDatabase
except ImportError:
    from vector_database.base_vector_database import BaseVectorDatabase

class FnBVectorDatabase(BaseVectorDatabase):
    def __init__(self):
        super().__init__(index_name="fnb-recommendations")
        # Override checkpoint file path to be specific for FnB
        self.checkpoint_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fnb_checkpoint.json')

    def prepare_fnb_embedding(self, data=None, incremental=True):
        """
        Prepare food and beverage embeddings with checkpoint support
        
        Args:
            data: Path to fnb_processed.csv file (default: None)
            incremental: If True, only generate embeddings for new items (default: True)
        """
        # Load data
        if data is None:
            data = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'fnb_processed.csv')
        
        # Check if data file exists    
        if not os.path.exists(data):
            # Create example data if file doesn't exist
            print(f"Data file not found at: {data}")
            print("Creating example data file...")
            
            # Check if data directory exists
            data_dir = os.path.dirname(data)
            if not os.path.exists(data_dir):
                print(f"Creating data directory: {data_dir}")
                os.makedirs(data_dir, exist_ok=True)
                
            # Create a small example dataset
            example_data = pd.DataFrame({
                'name': ['Phở Bát Đàn', 'Bún chả Hàng Mành', 'Cà phê Giảng'],
                'description': [
                    'Quán phở nổi tiếng tại Hà Nội với nước dùng đậm đà.',
                    'Quán bún chả truyền thống nổi tiếng với nước chấm thơm ngon.',
                    'Quán cà phê nổi tiếng với món cà phê trứng độc đáo.'
                ],
                'categories': ['Phở', 'Bún chả', 'Cà phê'],
                'price_range': ['50,000-80,000 VND', '40,000-70,000 VND', '25,000-45,000 VND'],
                'rating': [4.7, 4.5, 4.6],
                'menu_items': ['Phở bò, Phở gà, Phở nạm', 'Bún chả, Nem rán, Chả cuốn', 'Cà phê trứng, Cà phê đen, Cà phê sữa']
            })
            
            # Save example data
            example_data.to_csv(data, index=False)
            print(f"Created example data file at: {data}")
            
        print("Loading and processing FnB data...")
        print(f"Loading data from: {data}")
        raw_df = pd.read_csv(data)
        
        text_columns = ['name', 'description', 'categories', 'menu_items']
        for col in text_columns:
            if col in raw_df.columns:
                raw_df[col] = raw_df[col].fillna('')
        
        print("Processing prices...")
        if 'price_range' in raw_df.columns:
            raw_df['price_range'] = raw_df['price_range'].fillna('')
        
        print("Processing ratings...")
        if 'rating' in raw_df.columns:
            raw_df['rating'].fillna(raw_df[ơ'rating'].mean(), inplace=True)
            raw_df['rating'] = raw_df['rating'].astype(float)

        print("Generating indices...")
        if 'index' not in raw_df.columns:
            raw_df['index'] = ['fnb_' + str(i).zfill(6) for i in range(1, len(raw_df) + 1)]
        
        existing_df = None
        rows_to_embed = raw_df
        
        if incremental:
            # Check for existing embedding file
            embedding_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         'data', 'fnb_processed_embedding.csv')
            
            if os.path.exists(embedding_file):
                print(f"Found existing embedding file: {embedding_file}")
                existing_df = pd.read_csv(embedding_file)
                
                # Use base class method to find missing embeddings
                rows_to_embed, existing_df = self.find_missing_embeddings(
                    new_df=raw_df,
                    existing_df=existing_df,
                    id_field="index"
                )
                
                if len(rows_to_embed) == 0:
                    print("No new rows to embed. Using existing embeddings.")
                    self.df = existing_df
                    return
        
        print(f"Creating context strings for {len(rows_to_embed)} items...")
        rows_to_embed['context'] = [f'''
                                Đây là mô tả của nhà hàng/quán ăn:
                                {row['description']}
                                Danh mục của nó là {row.get('categories', '')}
                                Mức giá của nó là {row.get('price_range', '')}
                                Điểm đánh giá của nó là {row.get('rating', '')}
                                Một số món ăn nổi bật: {row.get('menu_items', '')}
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
            existing_indices = set(rows_to_embed['index'].astype(str))
            filtered_existing_df = existing_df[~existing_df['index'].astype(str).isin(existing_indices)]
            
            # Concatenate the filtered existing data with the new data
            final_df = pd.concat([filtered_existing_df, rows_to_embed], ignore_index=True)
            print(f"Combined {len(rows_to_embed)} new embeddings with {len(filtered_existing_df)} existing embeddings")

        # Save to the same directory as the input file
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'fnb_processed_embedding.csv')
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
                                     'data', 'fnb_processed_embedding.csv')
            
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
            self.prepare_fnb_embedding(incremental=False)
            
            if not os.path.exists(embedding_file):
                raise ValueError(f"Failed to create embedding file at {embedding_file}")
        
        # Load data from CSV
        print(f"Loading embeddings from: {embedding_file}")
        self.df = pd.read_csv(embedding_file)
        text_columns = ['name', 'description', 'categories', 'menu_items']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('')
                
        if not hasattr(self, 'df') or 'context_embedding' not in self.df.columns:
            raise ValueError("DataFrame not prepared or missing embeddings. Please run prepare_fnb_embedding first.")
            
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
                    "price_range": row.get("price_range", ""),
                    "rating": row.get("rating", 0),
                    "description": row["description"],
                    "menu_items": row.get("menu_items", ""),
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

    def get_fnb_by_id(self, fnb_id):
        """
        Retrieve a specific FnB by its ID
        """
        return self.get_item_by_id(fnb_id)
    
    def update_fnb(self, fnb_id, new_data):
        """
        Update FnB information in the database
        """
        def generate_fnb_context(metadata):
            """Generate context for FnB embedding"""
            return f'''
                Đây là mô tả của nhà hàng/quán ăn:
                {metadata['description']}
                Danh mục của nó là {metadata.get('categories', '')}
                Mức giá của nó là {metadata.get('price_range', '')}
                Điểm đánh giá của nó là {metadata.get('rating', '')}
                Một số món ăn nổi bật: {metadata.get('menu_items', '')}
            '''
        
        # Check if we need to generate new context and embedding
        needs_new_context = any(key in new_data for key in ['description', 'categories', 'price_range', 'rating', 'menu_items'])
        
        # Use the base class update_item method with our custom context generator
        return self.update_item(
            fnb_id, 
            new_data, 
            generate_context_func=generate_fnb_context if needs_new_context else None
        )
    
    def delete_fnb(self, fnb_id):
        """
        Delete FnB from the database
        """
        return self.delete_item(fnb_id)
    
    def get_all_fnbs(self, limit=1000):
        """
        Get all FnBs in the database (with pagination)
        """
        return self.get_all_items(limit)
    
    def search_by_category(self, category, top_k=5):
        """
        Search for FnBs by category
        """
        try:
            # Get all FnBs and filter by category
            all_fnbs = self.get_all_fnbs()
            filtered_fnbs = [
                match for match in all_fnbs['matches']
                if category.lower() in match['metadata']['categories'].lower()
            ]
            
            return {'matches': filtered_fnbs[:top_k]}
        except Exception as e:
            print(f"Error searching by category: {e}")
            return None
    
    def search_by_menu_item(self, item_name, top_k=5):
        """
        Search for FnBs that have a specific menu item
        """
        try:
            # Get all FnBs and filter by menu item
            all_fnbs = self.get_all_fnbs()
            filtered_fnbs = [
                match for match in all_fnbs['matches']
                if item_name.lower() in match['metadata']['menu_items'].lower()
            ]
            
            return {'matches': filtered_fnbs[:top_k]}
        except Exception as e:
            print(f"Error searching by menu item: {e}")
            return None
    
    def search_by_price_range(self, price_range, top_k=5):
        """
        Search for FnBs with a specific price range
        """
        try:
            # Get all FnBs and filter by price range
            all_fnbs = self.get_all_fnbs()
            filtered_fnbs = [
                match for match in all_fnbs['matches']
                if price_range.lower() in match['metadata']['price_range'].lower()
            ]
            
            return {'matches': filtered_fnbs[:top_k]}
        except Exception as e:
            print(f"Error searching by price range: {e}")
            return None
    
    def search_by_rating(self, min_rating, top_k=5):
        """
        Search for FnBs with minimum rating
        """
        try:
            # Get all FnBs and filter by rating
            all_fnbs = self.get_all_fnbs()
            filtered_fnbs = [
                match for match in all_fnbs['matches']
                if float(match['metadata']['rating']) >= float(min_rating)
            ]
            
            return {'matches': filtered_fnbs[:top_k]}
        except Exception as e:
            print(f"Error searching by rating: {e}")
            return None

    def get_fnb_ids(self, query_text, top_k=5):
        """
        Get FnB IDs from query results
        """
        ids, _ = self.query(query_text, top_k=top_k)
        return ids

def main():
    parser = argparse.ArgumentParser(description='Vector Database for FnB Recommendations')
    parser.add_argument('--prepare-data', action='store_true', help='Prepare and process FnB data')
    parser.add_argument('--no-incremental', action='store_true', help='Reprocess all data even if embeddings exist')
    parser.add_argument('--setup-pinecone', action='store_true', help='Setup Pinecone database')
    parser.add_argument('--insert-data', action='store_true', help='Insert data into Pinecone')
    parser.add_argument('--incremental', action='store_true', help='Use incremental update for data insertion')
    parser.add_argument('--query', type=str, help='Query text to search for similar FnBs')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    args = parser.parse_args()

    vector_db = FnBVectorDatabase()
    
    if args.prepare_data:
        vector_db.prepare_fnb_embedding(incremental=not args.no_incremental)
    
    if args.setup_pinecone:
        vector_db.set_up_pinecone()
        if args.insert_data:
            vector_db.load_data_to_pinecone(incremental=args.incremental)
        
    if args.query:
        # Check if Pinecone is set up, if not, set it up first
        if not vector_db.index:
            print("Pinecone index not initialized. Setting up now...")
            if not vector_db.set_up_pinecone():
                print("Failed to setup Pinecone. Please run prepare_fnb_embedding first.")
                return
            
        fnb_ids, results = vector_db.query(args.query, top_k=args.top_k)
        print("FnB IDs:")
        for fnb_id in fnb_ids:
            print(fnb_id)
        print("\nFull results:")
        for match in results['matches']:
            print(f"Name: {match['metadata']['name']}")
            print(f"Categories: {match['metadata']['categories']}")
            print(f"Price Range: {match['metadata']['price_range']}")
            print(f"Rating: {match['metadata']['rating']}")
            print(f"Description: {match['metadata']['description']}")
            print(f"Menu Items: {match['metadata']['menu_items']}")
            print("-" * 50)

if __name__ == "__main__":
    main() 