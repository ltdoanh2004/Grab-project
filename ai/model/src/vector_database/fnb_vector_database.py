import argparse
from tqdm import tqdm
import os
import pandas as pd
from typing import Dict, Any

from .base_vector_database import BaseVectorDatabase

class FnBVectorDatabase(BaseVectorDatabase):
    def __init__(self):
        super().__init__(index_name="fnb-recommendations")

    def prepare_fnb_embedding(self, data=None):
        """
        Prepare food and beverage embeddings with checkpoint support
        """
        # Load data
        if data is None:
            data = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'fnb_processed.csv')
            
        print("Loading and processing FnB data...")
        print(f"Loading data from: {data}")
        self.df = pd.read_csv(data)
        
        # Replace NaN values with empty strings for text columns
        text_columns = ['name', 'description', 'categories', 'menu_items']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('')
        
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        last_processed = checkpoint["last_processed_index"]
        existing_embeddings = checkpoint["embeddings"]
        
        print(f"Resuming from index {last_processed + 1} out of {len(self.df)} total rows")
        
        print("Processing prices...")
        if 'price_range' in self.df.columns:
            self.df['price_range'] = self.df['price_range'].fillna('')
        
        print("Processing ratings...")
        if 'rating' in self.df.columns:
            self.df['rating'].fillna(self.df['rating'].mean(), inplace=True)
            self.df['rating'] = self.df['rating'].astype(float)

        print("Generating indices...")
        self.df['index'] = ['fnb_' + str(i).zfill(5) for i in range(1, len(self.df) + 1)]

        print("Creating context strings...")
        self.df['context'] = [f'''
                                Đây là mô tả của nhà hàng/quán ăn:
                                {row['description']}
                                Danh mục của nó là {row.get('categories', '')}
                                Mức giá của nó là {row.get('price_range', '')}
                                Điểm đánh giá của nó là {row.get('rating', '')}
                                Một số món ăn nổi bật: {row.get('menu_items', '')}
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
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'fnb_processed_embedding.csv')
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
        self.df = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'fnb_processed_embedding.csv'))
        text_columns = ['name', 'description', 'categories', 'menu_items']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('')
                
        if not hasattr(self, 'df') or 'context_embedding' not in self.df.columns:
            raise ValueError("DataFrame not prepared or missing embeddings. Please run prepare_fnb_embedding first.")
            
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
    parser.add_argument('--setup-pinecone', action='store_true', help='Setup Pinecone database')
    parser.add_argument('--insert-data', action='store_true', help='Insert data into Pinecone')
    parser.add_argument('--query', type=str, help='Query text to search for similar FnBs')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    args = parser.parse_args()

    vector_db = FnBVectorDatabase()
    
    if args.prepare_data:
        vector_db.prepare_fnb_embedding()
    
    if args.setup_pinecone:
        vector_db.set_up_pinecone()
        if args.insert_data:
            vector_db.load_data_to_pinecone()
        
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