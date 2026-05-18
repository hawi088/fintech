"""
Data-Driven Thematic Analysis
No hardcoded themes - let the data speak for itself
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import defaultdict, Counter
import re

def load_data():
    df = pd.read_csv('data/sentiment_results_distilbert.csv')
    print(f" Loaded {len(df)} reviews")
    return df

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

def extract_top_keywords(df, bank_name, n_keywords=20):
    """Extract top keywords from data (no hardcoding)"""
    
    bank_df = df[df['bank'] == bank_name]
    
    tfidf = TfidfVectorizer(
        max_features=50,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    tfidf_matrix = tfidf.fit_transform(bank_df['clean_review'])
    feature_names = tfidf.get_feature_names_out()
    scores = tfidf_matrix.mean(axis=0).tolist()[0]
    
    keywords = [(feature_names[i], scores[i]) for i in range(len(feature_names))]
    keywords.sort(key=lambda x: x[1], reverse=True)
    
    return keywords[:n_keywords]

def cluster_keywords_into_themes(keywords, n_themes=5):
    """
    Automatically cluster keywords into themes using KMeans
    This discovers themes from the data, not from hardcoded lists
    """
    
    if len(keywords) < n_themes:
        return {f"Theme {i+1}": [kw for kw, _ in keywords[i:i+3]] for i in range(len(keywords)//3 + 1)}
    
    # Create feature vectors for keywords (using word embeddings)
    from sklearn.feature_extraction.text import CountVectorizer
    
    # Get just the keyword strings
    keyword_texts = [kw for kw, _ in keywords]
    
    # Vectorize keywords
    vectorizer = CountVectorizer(analyzer='char', ngram_range=(2, 4))
    X = vectorizer.fit_transform(keyword_texts)
    
    # Cluster
    kmeans = KMeans(n_clusters=min(n_themes, len(keywords)//2), random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)
    
    # Group keywords by cluster
    theme_keywords = defaultdict(list)
    for idx, (kw, score) in enumerate(keywords):
        theme_keywords[f"Theme {clusters[idx] + 1}"].append(kw)
    
    # Rename themes based on most common keywords
    themed_results = {}
    for theme_name, kw_list in theme_keywords.items():
        # Create descriptive name from top keywords
        top_kw = kw_list[:3]
        if len(top_kw) == 3:
            descriptive_name = f"{top_kw[0]}, {top_kw[1]}, {top_kw[2]}"
        elif len(top_kw) == 2:
            descriptive_name = f"{top_kw[0]}, {top_kw[1]}"
        else:
            descriptive_name = top_kw[0] if top_kw else "misc"
        
        # Capitalize first letter
        descriptive_name = descriptive_name.title()
        themed_results[descriptive_name] = kw_list
    
    return themed_results

def analyze_bank_data_driven(df, bank_name):
    """Complete data-driven analysis for a bank"""
    
    print(f"\n{'='*50}")
    print(f" {bank_name}")
    print(f"{'='*50}")
    
    bank_df = df[df['bank'] == bank_name]
    
    # Positive reviews keywords
    pos_df = bank_df[bank_df['sentiment_label'] == 'POSITIVE']
    neg_df = bank_df[bank_df['sentiment_label'] == 'NEGATIVE']
    
    print(f"Total: {len(bank_df)} | Positive: {len(pos_df)} | Negative: {len(neg_df)}")
    
    # Get keywords from ALL reviews
    all_keywords = extract_top_keywords(df, bank_name, 30)
    print(f"\n Top keywords from all reviews:")
    for kw, score in all_keywords[:15]:
        print(f"   - {kw}: {score:.4f}")
    
    # Positive keywords (what users like)
    if len(pos_df) > 10:
        pos_keywords = extract_top_keywords(pos_df, bank_name, 15)
        print(f"\n Users LIKE (Positive keywords):")
        for kw, score in pos_keywords[:10]:
            print(f"   - {kw}: {score:.4f}")
    
    # Negative keywords (what users complain about)
    if len(neg_df) > 10:
        neg_keywords = extract_top_keywords(neg_df, bank_name, 15)
        print(f"\n Users COMPLAIN about (Negative keywords):")
        for kw, score in neg_keywords[:10]:
            print(f"   - {kw}: {score:.4f}")
    
    # Discover themes from all keywords
    print(f"\n DISCOVERED THEMES (from data):")
    themes = cluster_keywords_into_themes(all_keywords, n_themes=5)
    
    for theme_name, kw_list in themes.items():
        print(f"\n   {theme_name}:")
        for kw in kw_list[:8]:
            print(f"      - {kw}")
    
    return {
        'bank': bank_name,
        'keywords': all_keywords,
        'positive_keywords': pos_keywords if len(pos_df) > 10 else [],
        'negative_keywords': neg_keywords if len(neg_df) > 10 else [],
        'themes': themes
    }

def main():
    df = load_data()
    df['clean_review'] = df['review'].apply(clean_text)
    
    results = []
    for bank in df['bank'].unique():
        result = analyze_bank_data_driven(df, bank)
        results.append(result)
    
    # Generate markdown for report
    print("\n" + "="*60)
    print(" MARKDOWN FOR REPORT")
    print("="*60)
    
    for result in results:
        print(f"\n## {result['bank']}")
        print("\n### Top Keywords (Data-Driven)")
        for kw, score in result['keywords'][:10]:
            print(f"- {kw}")
        
        if result['positive_keywords']:
            print("\n###  What Users Like")
            for kw, score in result['positive_keywords'][:8]:
                print(f"- {kw}")
        
        if result['negative_keywords']:
            print("\n###  What Users Complain About")
            for kw, score in result['negative_keywords'][:8]:
                print(f"- {kw}")
        
        print("\n###  Discovered Themes")
        for theme, kw_list in result['themes'].items():
            print(f"\n**{theme}**")
            for kw in kw_list[:5]:
                print(f"  - {kw}")

if __name__ == "__main__":
    main()