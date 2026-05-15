"""
Google Play Store Review Scraper - WORKING VERSION
CBE, BOA, and Dashen Bank
"""

from google_play_scraper import reviews, Sort
import pandas as pd
import time
import os

# CORRECT APP IDs - WORKING
BANKS = {
    "CBE": "com.combanketh.mobilebanking",
    "BOA": "com.boa.boaMobileBanking",
    "Dashen": "com.dashen.dashensuperapp"
}

def scrape_bank(app_id, bank_name, target=500):
    """Scrape reviews for a single bank"""
    
    print(f"\nScraping {bank_name}...")
    
    all_reviews = []
    token = None
    
    while len(all_reviews) < target:
        try:
            result, token = reviews(
                app_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=100,
                continuation_token=token
            )
            
            if not result:
                break
                
            all_reviews.extend(result)
            print(f"  {bank_name}: {len(all_reviews)} reviews")
            
            if not token:
                break
                
            time.sleep(1)
            
        except Exception as e:
            print(f"  Error: {e}")
            break
    
    if not all_reviews:
        return pd.DataFrame()
    
    df = pd.DataFrame(all_reviews)
    df = df[['content', 'score', 'at', 'reviewId']]
    df.columns = ['review', 'rating', 'date', 'review_id']
    df['bank'] = bank_name
    df['source'] = 'Google Play'
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    print(f"   {bank_name}: {len(df)} reviews")
    return df

def scrape_all():
    """Scrape all three banks"""
    
    os.makedirs('data/raw', exist_ok=True)
    
    all_data = []
    
    for bank_name, app_id in BANKS.items():
        df = scrape_bank(app_id, bank_name, target=500)
        if not df.empty:
            all_data.append(df)
        time.sleep(2)
    
    if not all_data:
        print("No data collected")
        return None
    
    combined = pd.concat(all_data, ignore_index=True)
    
    # Save
    combined.to_csv('data/raw/all_reviews.csv', index=False)
    
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    print(combined['bank'].value_counts())
    print(f"\nTOTAL: {len(combined)} reviews")
    print("Saved to data/raw/all_reviews.csv")
    
    return combined

if __name__ == "__main__":
    scrape_all()