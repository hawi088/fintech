"""
Data Preprocessing for Bank Reviews
Handles duplicates, missing values, date normalization
"""

import pandas as pd
import os

def load_raw_data(file_path='data/raw/all_reviews.csv'):
    """Load raw scraped data"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raw data not found at {file_path}")
    
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} raw reviews")
    return df

def remove_duplicates(df):
    """Remove duplicate reviews by review_id"""
    initial_count = len(df)
    df = df.drop_duplicates(subset=['review_id'])
    removed = initial_count - len(df)
    print(f"Removed {removed} duplicate reviews")
    return df

def handle_missing_values(df):
    """Handle missing review text or rating"""
    initial_count = len(df)
    
    # Drop rows missing review text or rating
    df = df.dropna(subset=['review', 'rating'])
    
    dropped = initial_count - len(df)
    print(f"Dropped {dropped} rows with missing review or rating")
    return df

def normalize_dates(df):
    """Convert dates to YYYY-MM-DD format"""
    df['date'] = pd.to_datetime(df['date']).dt.date
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    return df

def clean_review_text(df):
    """Basic text cleaning for reviews"""
    # Remove extra whitespace
    df['review'] = df['review'].str.strip()
    return df

def save_cleaned_data(df, output_path='data/cleaned_reviews.csv'):
    """Save cleaned dataset"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Cleaned data saved to {output_path}")
    return df

def print_quality_report(df):
    """Print data quality summary"""
    print("\n" + "=" * 50)
    print("DATA QUALITY REPORT")
    print("=" * 50)
    
    # Total reviews by bank
    print("\nReviews per bank:")
    print(df['bank'].value_counts())
    
    # Rating distribution
    print("\nRating distribution:")
    print(df['rating'].value_counts().sort_index())
    
    # Missing values
    print("\nMissing values:")
    print(df.isnull().sum())
    
    # Date range
    print(f"\nDate range: {df['date'].min()} to {df['date'].max()}")

def main():
    """Main preprocessing pipeline"""
    print("=" * 50)
    print("Starting Data Preprocessing...")
    print("=" * 50)
    
    # Load
    df = load_raw_data()
    
    # Clean
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = normalize_dates(df)
    df = clean_review_text(df)
    
    # Validate minimum requirements
    reviews_per_bank = df['bank'].value_counts()
    for bank, count in reviews_per_bank.items():
        if count < 400:
            print(f"⚠️ Warning: {bank} has only {count} reviews (minimum 400 required)")
    
    # Save and report
    save_cleaned_data(df)
    print_quality_report(df)
    
    return df

if __name__ == "__main__":
    df_cleaned = main()