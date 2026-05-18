"""
PostgreSQL Database Setup for Bank Reviews
Creates banks and reviews tables
"""

import psycopg2
from psycopg2 import sql
import pandas as pd
from db_config import get_db_connection

def create_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**get_db_connection())
        print("Connected to PostgreSQL database")
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def create_tables(conn):
    """Create banks and reviews tables"""
    
    cur = conn.cursor()
    
    # Drop existing tables if they exist (for clean setup)
    cur.execute("DROP TABLE IF EXISTS reviews CASCADE")
    cur.execute("DROP TABLE IF EXISTS banks CASCADE")
    
    # Create banks table
    banks_table = """
    CREATE TABLE banks (
        bank_id SERIAL PRIMARY KEY,
        bank_name VARCHAR(50) NOT NULL UNIQUE,
        app_name VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cur.execute(banks_table)
    print("Created 'banks' table")
    
    # Create reviews table
    reviews_table = """
    CREATE TABLE reviews (
        review_id VARCHAR(100) PRIMARY KEY,
        bank_id INTEGER REFERENCES banks(bank_id),
        review_text TEXT NOT NULL,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        review_date DATE,
        sentiment_label VARCHAR(10),
        sentiment_score DECIMAL(5,4),
        identified_theme VARCHAR(100),
        source VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cur.execute(reviews_table)
    print("Created 'reviews' table")
    
    conn.commit()
    cur.close()

def insert_banks(conn):
    """Insert bank data into banks table"""
    
    cur = conn.cursor()
    
    banks = [
        ("CBE", "Commercial Bank of Ethiopia Mobile"),
        ("BOA", "Bank of Abyssinia Mobile"),
        ("Dashen", "Dashen Bank Super App")
    ]
    
    for bank_name, app_name in banks:
        cur.execute(
            "INSERT INTO banks (bank_name, app_name) VALUES (%s, %s) ON CONFLICT (bank_name) DO NOTHING",
            (bank_name, app_name)
        )
    
    conn.commit()
    cur.close()
    print("Inserted bank data")

def load_reviews_from_csv(conn, csv_path='data/thematic_pipeline_results.csv'):
    """Load reviews from CSV into database"""
    
    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} reviews from CSV")
        
        # Get bank_id mapping
        cur = conn.cursor()
        cur.execute("SELECT bank_name, bank_id FROM banks")
        bank_map = {row[0]: row[1] for row in cur.fetchall()}
        cur.close()
        
        # Insert reviews
        cur = conn.cursor()
        inserted = 0
        
        for _, row in df.iterrows():
            # Map bank name to bank_id
            # Check for bank column in various possible names
            bank_name = None
            for col in ['bank', 'bank_name', 'source_bank']:
                if col in row:
                    bank_name = row[col]
                    break
            
            if bank_name is None:
                print(f"Warning: No bank column found. Available columns: {list(df.columns)}")
                break
            
            bank_id = bank_map.get(bank_name)
            if bank_id is None:
                print(f"Warning: Unknown bank {bank_name}")
                continue
            
            # Get review text from possible column names
            review_text = row.get('review', row.get('review_text', ''))
            
            # Get review_id or generate one
            review_id = row.get('review_id', f"review_{_}")
            
            cur.execute("""
                INSERT INTO reviews 
                (review_id, bank_id, review_text, rating, review_date, 
                 sentiment_label, sentiment_score, identified_theme, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (review_id) DO NOTHING
            """, (
                review_id,
                bank_id,
                review_text,
                row.get('rating', None),
                row.get('date', row.get('review_date', None)),
                row.get('sentiment_label', 'NEUTRAL'),
                row.get('sentiment_score', 0.5),
                row.get('identified_theme', 'Other'),
                'Google Play'
            ))
            inserted += 1
        
        conn.commit()
        cur.close()
        print(f"Inserted {inserted} reviews into database")
        
    except FileNotFoundError:
        print(f" CSV file not found: {csv_path}")
        print("Skipping review insertion. Run your scraping pipeline first.")
    except Exception as e:
        print(f"Error loading reviews: {e}")

def verify_data(conn):
    """Run verification queries"""
    
    cur = conn.cursor()
    
    print("\n" + "="*50)
    print("DATABASE VERIFICATION")
    print("="*50)
    
    # Count reviews per bank
    cur.execute("""
        SELECT b.bank_name, COUNT(r.review_id) as review_count
        FROM banks b
        LEFT JOIN reviews r ON b.bank_id = r.bank_id
        GROUP BY b.bank_name
        ORDER BY b.bank_name
    """)
    print("\n Reviews per bank:")
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]} reviews")
    
    # Average rating per bank (only where rating exists)
    cur.execute("""
        SELECT b.bank_name, ROUND(AVG(r.rating), 2) as avg_rating
        FROM banks b
        JOIN reviews r ON b.bank_id = r.bank_id
        WHERE r.rating IS NOT NULL
        GROUP BY b.bank_name
        ORDER BY b.bank_name
    """)
    print("\n Average rating per bank:")
    for row in cur.fetchall():
        rating = row[1]
        if rating is not None:
            print(f"   {row[0]}: {rating:.2f} stars")
        else:
            print(f"   {row[0]}: No ratings available")
    
    # Sentiment distribution
    cur.execute("""
        SELECT sentiment_label, COUNT(*) 
        FROM reviews 
        GROUP BY sentiment_label
        ORDER BY COUNT(*) DESC
    """)
    print("\n Sentiment distribution:")
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]}")
    
    # Theme distribution
    cur.execute("""
        SELECT identified_theme, COUNT(*) 
        FROM reviews 
        WHERE identified_theme IS NOT NULL
        GROUP BY identified_theme
        ORDER BY COUNT(*) DESC
        LIMIT 5
    """)
    print("\n Top 5 themes:")
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]}")
    
    # Total reviews
    cur.execute("SELECT COUNT(*) FROM reviews")
    total = cur.fetchone()[0]
    print(f"\n Total reviews in database: {total}")
    
    # NULL CHECK - Fixed indentation
    print("\n NULL CHECK:")
    cur.execute("""
        SELECT 
            COUNT(*) as total_reviews,
            SUM(CASE WHEN review_text IS NULL THEN 1 ELSE 0 END) as null_review_text,
            SUM(CASE WHEN sentiment_label IS NULL THEN 1 ELSE 0 END) as null_sentiment,
            SUM(CASE WHEN bank_id IS NULL THEN 1 ELSE 0 END) as null_bank_id,
            SUM(CASE WHEN rating IS NULL THEN 1 ELSE 0 END) as null_rating
        FROM reviews
    """)
    result = cur.fetchone()
    print(f"   Total reviews: {result[0]}")
    print(f"   Missing review_text: {result[1]}")
    print(f"   Missing sentiment: {result[2]}")
    print(f"   Missing bank_id: {result[3]}")
    print(f"   Missing rating: {result[4]}")
    
    cur.close()

def main():
    print(" POSTGRESQL DATABASE SETUP")
   
    
    # Connect to database
    conn = create_connection()
    if conn is None:
        return
    
    # Create tables
    create_tables(conn)
    
    # Insert banks
    insert_banks(conn)
    
    # Load reviews from CSV
    load_reviews_from_csv(conn)
    
    # Verify data
    verify_data(conn)
    
    # Close connection
    conn.close()
    print("\nDatabase setup complete!")

if __name__ == "__main__":
    main()