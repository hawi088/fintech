"""
Modular Thematic Analysis Pipeline - DATA DRIVEN
No hardcoded themes - themes discovered from keyword clustering
Handles: tokenization, stop-word removal, lemmatization, theme extraction
Output: CSV with review_id, review_text, sentiment_label, sentiment_score, identified_theme
"""

import pandas as pd
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data (first time only)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class TextPreprocessor:
    """Handles tokenization, stop-word removal, and lemmatization"""
    
    def __init__(self, use_lemmatization=True):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.use_lemmatization = use_lemmatization
    
    def clean_text(self, text):
        """Basic text cleaning"""
        if pd.isna(text):
            return ""
        text = str(text).lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def tokenize(self, text):
        """Tokenize text into words"""
        return word_tokenize(text)
    
    def remove_stopwords(self, tokens):
        """Remove common English stopwords"""
        return [token for token in tokens if token not in self.stop_words and len(token) > 2]
    
    def lemmatize(self, tokens):
        """Lemmatize tokens to base form"""
        if self.use_lemmatization:
            return [self.lemmatizer.lemmatize(token) for token in tokens]
        return tokens
    
    def preprocess(self, text):
        """Full preprocessing pipeline"""
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        tokens_no_stop = self.remove_stopwords(tokens)
        final_tokens = self.lemmatize(tokens_no_stop)
        return final_tokens
    
    def preprocess_to_string(self, text):
        """Preprocess and return as space-separated string"""
        tokens = self.preprocess(text)
        return ' '.join(tokens)

class DataDrivenThemeExtractor:
    """
    Discovers themes dynamically from keywords using clustering
    NO HARDCODED THEMES
    """
    
    def __init__(self, preprocessor, n_themes=5):
        self.preprocessor = preprocessor
        self.n_themes = n_themes
        self.theme_keywords = {}  # Will be populated from data
        self.tfidf = TfidfVectorizer(max_features=50, stop_words='english', ngram_range=(1, 2))
    
    def extract_all_keywords(self, df):
        """Extract keywords from all reviews combined"""
        processed_texts = df['clean_review'].tolist()
        
        if len(processed_texts) < 10:
            return []
        
        tfidf_matrix = self.tfidf.fit_transform(processed_texts)
        feature_names = self.tfidf.get_feature_names_out()
        scores = tfidf_matrix.mean(axis=0).tolist()[0]
        
        keywords = [(feature_names[i], scores[i]) for i in range(len(feature_names))]
        keywords.sort(key=lambda x: x[1], reverse=True)
        
        return keywords[:50]  # Top 50 keywords
    
    def discover_themes_from_keywords(self, keywords):
        """
        Discover themes by clustering keywords
        Returns: dictionary of theme names -> list of keywords
        """
        if len(keywords) < self.n_themes:
            return {"General Themes": [kw for kw, _ in keywords]}
        
        # Create feature matrix from keywords (using character n-grams for similarity)
        keyword_texts = [kw for kw, _ in keywords]
        
        # Vectorize keywords using character n-grams (captures word structure)
        from sklearn.feature_extraction.text import CountVectorizer
        vectorizer = CountVectorizer(analyzer='char', ngram_range=(2, 4))
        X = vectorizer.fit_transform(keyword_texts)
        
        # Cluster keywords
        n_clusters = min(self.n_themes, len(keywords) // 3)
        if n_clusters < 2:
            return {"General Themes": [kw for kw, _ in keywords]}
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X)
        
        # Group keywords by cluster
        theme_groups = defaultdict(list)
        for idx, (kw, score) in enumerate(keywords):
            theme_groups[f"Theme {clusters[idx] + 1}"].append(kw)
        
        # Rename themes based on most frequent words
        renamed_themes = {}
        for theme_name, kw_list in theme_groups.items():
            # Take top 3 keywords as theme description
            top_keywords = kw_list[:3]
            if len(top_keywords) == 3:
                desc = f"{top_keywords[0]}, {top_keywords[1]}, {top_keywords[2]}"
            elif len(top_keywords) == 2:
                desc = f"{top_keywords[0]}, {top_keywords[1]}"
            else:
                desc = top_keywords[0] if top_keywords else "misc"
            desc = desc.title()
            renamed_themes[desc] = kw_list
        
        return renamed_themes
    
    def assign_theme_to_review(self, review_text, theme_keywords_map):
        """Assign theme based on keyword matching (data-driven)"""
        review_lower = review_text.lower()
        
        for theme, keywords in theme_keywords_map.items():
            for keyword in keywords:
                if keyword in review_lower:
                    return theme
        
        return "Other"
    
    def fit(self, df):
        """Learn themes from the data"""
        print("\n Discovering themes from data...")
        
        # Extract all keywords
        keywords = self.extract_all_keywords(df)
        print(f"   Extracted {len(keywords)} keywords")
        
        # Discover themes
        self.theme_keywords = self.discover_themes_from_keywords(keywords)
        
        print(f"\n   Discovered {len(self.theme_keywords)} themes:")
        for theme, keywords in self.theme_keywords.items():
            print(f"      - {theme}: {', '.join(keywords[:5])}...")
        
        return self
    
    def get_theme_for_review(self, review_text):
        """Get theme for a single review"""
        if not self.theme_keywords:
            return "Not Fitted"
        return self.assign_theme_to_review(review_text, self.theme_keywords)
    
    def get_bank_specific_themes(self, df, bank_name):
        """Discover themes specific to a bank"""
        bank_df = df[df['bank'] == bank_name]
        if len(bank_df) < 20:
            return {}
        
        # Extract keywords for this bank
        processed_texts = bank_df['clean_review'].tolist()
        tfidf = TfidfVectorizer(max_features=30, stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = tfidf.fit_transform(processed_texts)
        feature_names = tfidf.get_feature_names_out()
        scores = tfidf_matrix.mean(axis=0).tolist()[0]
        
        keywords = [(feature_names[i], scores[i]) for i in range(len(feature_names))]
        keywords.sort(key=lambda x: x[1], reverse=True)
        keywords = keywords[:25]
        
        # Discover bank-specific themes
        return self.discover_themes_from_keywords(keywords)


class ThematicPipeline:
    """Complete pipeline that processes reviews and saves results"""
    
    def __init__(self, use_lemmatization=True, n_themes=5):
        self.preprocessor = TextPreprocessor(use_lemmatization=use_lemmatization)
        self.theme_extractor = DataDrivenThemeExtractor(self.preprocessor, n_themes=n_themes)
    
    def load_data(self, file_path='data/sentiment_results_distilbert.csv'):
        """Load sentiment results"""
        df = pd.read_csv(file_path)
        print(f" Loaded {len(df)} reviews")
        return df
    
    def preprocess_reviews(self, df):
        """Apply preprocessing to all reviews"""
        print("\n Preprocessing reviews...")
        df['clean_review'] = df['review'].apply(self.preprocessor.preprocess_to_string)
        print(f"   Preprocessed {len(df)} reviews")
        return df
    
    def fit_themes(self, df):
        """Learn themes from all reviews (data-driven)"""
        self.theme_extractor.fit(df)
        return self
    
    def assign_themes(self, df):
        """Assign themes to all reviews"""
        print("\n Assigning themes to reviews...")
        df['identified_theme'] = df['review'].apply(self.theme_extractor.get_theme_for_review)
        
        # Print theme distribution
        theme_counts = df['identified_theme'].value_counts()
        print("\n   Theme distribution (all banks):")
        for theme, count in theme_counts.items():
            print(f"      {theme}: {count} ({count/len(df)*100:.1f}%)")
        
        return df
    
    def extract_bank_specific_themes(self, df):
        """Extract and print themes specific to each bank"""
        print("\nBank-Specific Themes (Data-Driven):")
        
        for bank in df['bank'].unique():
            bank_themes = self.theme_extractor.get_bank_specific_themes(df, bank)
            print(f"\n    {bank}:")
            if bank_themes:
                for theme, keywords in bank_themes.items():
                    print(f"      - {theme}: {', '.join(keywords[:3])}")
            else:
                print(f"      - Insufficient data for theme discovery")
    
    def save_results(self, df, output_path='data/thematic_pipeline_results.csv'):
        """Save results with required columns"""
        output_df = df[['review_id', 'review', 'sentiment_label', 'sentiment_score', 'identified_theme']]
        output_df.to_csv(output_path, index=False)
        print(f"\n Results saved to: {output_path}")
        print(f"   Columns: {output_df.columns.tolist()}")
        return output_df
    
    def print_sample(self, df, n=10):
        """Print sample of results"""

        print(" SAMPLE RESULTS")
    
        
        sample = df[['review', 'sentiment_label', 'identified_theme']].head(n)
        for idx, row in sample.iterrows():
            review_short = row['review'][:80] + '...' if len(row['review']) > 80 else row['review']
            print(f"\nReview: {review_short}")
            print(f"Sentiment: {row['sentiment_label']} | Theme: {row['identified_theme']}")
    
    def run(self):
        """Execute the complete pipeline"""

        print("🎯 DATA-DRIVEN THEMATIC ANALYSIS PIPELINE")
        
        # Step 1: Load data
        df = self.load_data()
        
        # Step 2: Preprocess reviews
        df = self.preprocess_reviews(df)
        
        # Step 3: Learn themes from data
        self.fit_themes(df)
        
        # Step 4: Assign themes to reviews
        df = self.assign_themes(df)
        
        # Step 5: Extract bank-specific themes
        self.extract_bank_specific_themes(df)
        
        # Step 6: Save results
        output_df = self.save_results(df)
        
        # Step 7: Print sample
        self.print_sample(df)
        
      
        print("PIPELINE COMPLETE")
        return output_df

if __name__ == "__main__":
    pipeline = ThematicPipeline(use_lemmatization=True, n_themes=5)
    results = pipeline.run()