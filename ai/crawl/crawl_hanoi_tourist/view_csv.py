import pandas as pd
import os

def view_csv():
    # File path
    csv_file = os.path.join('data', 'processed_tours.csv')
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File {csv_file} not found!")
        return
    
    # Read CSV file
    print(f"Reading CSV file: {csv_file}")
    df = pd.read_csv(csv_file)
    
    # Display basic information
    print(f"\nTotal tours: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Check if location column exists
    if 'location' in df.columns:
        print("\n=== Location Information ===")
        
        # Count unique locations
        unique_locations = df['location'].nunique()
        print(f"Number of unique location values: {unique_locations}")
        
        # Display top locations
        print("\nTop 10 locations by frequency:")
        # Split combined locations and count each occurrence
        location_counts = {}
        
        for loc in df['location']:
            if pd.isna(loc):
                continue
                
            if "," in str(loc):
                # Split multiple locations and count each
                for single_loc in str(loc).split(", "):
                    location_counts[single_loc] = location_counts.get(single_loc, 0) + 1
            else:
                location_counts[str(loc)] = location_counts.get(str(loc), 0) + 1
        
        # Display top locations
        for location, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {location}: {count} tours")
    
    # Display sample data
    print("\n=== Sample Data (First 5 rows) ===")
    sample_columns = ['name', 'location', 'category', 'days', 'price']
    sample_df = df[sample_columns].head()
    print(sample_df.to_string(index=False))
    
    # Show some statistics
    if 'price' in df.columns:
        print("\n=== Price Statistics ===")
        # Convert to numeric, ignoring errors
        df['price_numeric'] = pd.to_numeric(df['price'], errors='coerce')
        
        print(f"Min price: {df['price_numeric'].min():,.0f} VND")
        print(f"Max price: {df['price_numeric'].max():,.0f} VND")
        print(f"Average price: {df['price_numeric'].mean():,.0f} VND")
    
    # For locations per category
    if 'category' in df.columns and 'location' in df.columns:
        print("\n=== Top Locations per Category ===")
        
        # Group by category
        for category in df['category'].unique():
            print(f"\nCategory: {category}")
            # Get tours for this category
            category_tours = df[df['category'] == category]
            
            # Count locations
            cat_location_counts = {}
            
            for loc in category_tours['location']:
                if pd.isna(loc):
                    continue
                    
                if "," in str(loc):
                    # Split multiple locations and count each
                    for single_loc in str(loc).split(", "):
                        cat_location_counts[single_loc] = cat_location_counts.get(single_loc, 0) + 1
                else:
                    cat_location_counts[str(loc)] = cat_location_counts.get(str(loc), 0) + 1
            
            # Display top locations for this category
            for location, count in sorted(cat_location_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"  - {location}: {count} tours")

if __name__ == "__main__":
    view_csv() 