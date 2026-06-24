import os
import pandas as pd
import numpy as np

def generate_mock_messy_data():
    """Generates a dataset simulating the exact flaws from the project brief."""
    data = {
        'Order_ID': ['#44902', '#44902', '#44903', '#44904', '#44905', '#44905'],
        'Product': ['Nexus-X', 'Nexus-X', 'Quantum-S', 'Aero-Z', 'Nexus-X', 'Nexus-X'],
        'Qty': [3, 3, np.nan, 1, 2, 2],
        'Value': [1499.97, 1499.97, 499.99, np.nan, 999.98, 999.98],
        'City': ['Bangalore', 'BLR', ' MUMBAI ', 'mumbai', 'Bengaluru', 'Puducherry'],
        'Timestamp': ['2024-01-15T14:32:21Z', '2024-01-15T14:32:21Z', '16/01/2024', '2024-01-17', '2024-01-18 15:00:00', '2024-01-18 15:00:00']
    }
    df = pd.DataFrame(data)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/raw_data.csv', index=False)
    print("✔ Successfully created simulated 'data/raw_data.csv'")

def clean_dataset():
    print("\n--- Initializing DecodeLabs Data Integrity Audit ---")
    
    # 1. Load the dataset
    if not os.path.exists('data/raw_data.csv'):
        generate_mock_messy_data()
        
    df = pd.read_csv('data/raw_data.csv')
    print(f"📊 Raw shape: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # 2. Phase 1: Strategic Imputation (Handle Gaps without listwise deletion)
    print("\n[Phase 1] Handling missing values strategically...")
    # Numeric values: Impute Qty using Mode (counts are usually discrete), Value using Median
    if df['Qty'].isnull().any():
        qty_mode = df['Qty'].mode()[0]
        df['Qty'] = df['Qty'].fillna(qty_mode)
        print(f"   Imputed missing Qty with Mode: {qty_mode}")
        
    if df['Value'].isnull().any():
        val_median = df['Value'].median()
        df['Value'] = df['Value'].fillna(val_median)
        print(f"   Imputed missing Value with Median: {val_median}")

    # 3. Phase 2: Integrity Audit (Eliminate duplicates based on Order_ID)
    print("\n[Phase 2] Executing duplication audit...")
    # Clean string identifier markers if any exist
    df['Order_ID'] = df['Order_ID'].astype(str).str.replace('#', '').str.strip()
    
    initial_count = len(df)
    df = df.drop_duplicates(subset=['Order_ID'], keep='first')
    print(f"   Removed {initial_count - len(df)} duplicate records based on Order_ID.")

    # 4. Phase 3: Speak One Language (Format Dates & Standardize text strings)
    print("\n[Phase 3] Enforcing alignment, schema consistency, and ISO standards...")
    
    # Standardize Cities mapping structural anomalies to absolute regional names
    city_mapping = {
        'Bangalore': 'Bengaluru', 'BLR': 'Bengaluru', 'Bengaluru': 'Bengaluru',
        'MUMBAI': 'Mumbai', 'mumbai': 'Mumbai', 'Puducherry': 'Puducherry'
    }
    df['City'] = df['City'].astype(str).str.strip().map(lambda x: city_mapping.get(x, x.title()))
    
    # Correct Date Formats to valid ISO 8601 strings (YYYY-MM-DD)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # Ensure Numeric Precision (2 Decimals)
    df['Value'] = df['Value'].round(2)
    df['Qty'] = df['Qty'].astype(int)

    # 5. Export Processed Data
    output_path = 'data/clean_data.csv'
    df.to_csv(output_path, index=False)
    print(f"\n✨ Golden Standard achieved! Clean data saved to: {output_path}")
    print(f"📊 Post-cleaning shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
    print(df.to_string(index=False))

if __name__ == "__main__":
    clean_dataset()