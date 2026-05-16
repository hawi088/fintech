"""
Sentiment Analysis using DistilBERT
Based on: https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english
"""

import pandas as pd
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from tqdm import tqdm
import time

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

def load_model_and_tokenizer():
    """
    Load the DistilBERT model and tokenizer as per Hugging Face documentation
    """
    print(" Loading DistilBERT model and tokenizer...")
    
    # Load tokenizer
    tokenizer = DistilBertTokenizer.from_pretrained(
        "distilbert-base-uncased-finetuned-sst-2-english"
    )
    
    # Load model
    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased-finetuned-sst-2-english"
    )
    
    # Move model to GPU if available
    model = model.to(device)
    model.eval()  # Set to evaluation mode
    
    # Get label mapping
    labels = model.config.id2label  # {0: 'NEGATIVE', 1: 'POSITIVE'}
    
    print(f" Model loaded successfully!")
    print(f"   Label mapping: {labels}")
    
    return tokenizer, model, labels

def predict_sentiment_batch(reviews, tokenizer, model, batch_size=32):
    """
    Predict sentiment for a batch of reviews using DistilBERT
    
    Returns:
        - sentiment_label: 'POSITIVE', 'NEGATIVE', or 'NEUTRAL'
        - confidence_score: probability of the predicted class
    """
    
    # Tokenize all reviews
    encoded_inputs = tokenizer(
        reviews,
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors="pt"
    )
    
    # Move inputs to device
    input_ids = encoded_inputs['input_ids'].to(device)
    attention_mask = encoded_inputs['attention_mask'].to(device)
    
    # Create TensorDataset
    dataset = TensorDataset(input_ids, attention_mask)
    dataloader = DataLoader(dataset, batch_size=batch_size)
    
    all_logits = []
    
    with torch.no_grad():  # Disable gradient calculation for inference
        for batch_input_ids, batch_attention_mask in tqdm(dataloader, desc="Processing batches"):
            # Forward pass
            outputs = model(
                input_ids=batch_input_ids,
                attention_mask=batch_attention_mask
            )
            logits = outputs.logits
            all_logits.append(logits.cpu())
    
    # Concatenate all logits
    all_logits = torch.cat(all_logits, dim=0)
    
    # Get probabilities using softmax
    probabilities = torch.softmax(all_logits, dim=1)
    
    # Get predicted class and confidence
    predicted_class_ids = torch.argmax(all_logits, dim=1)
    confidences = probabilities[range(len(probabilities)), predicted_class_ids]
    
    # Convert to labels
    sentiment_labels = []
    for class_id, confidence in zip(predicted_class_ids, confidences):
        sentiment = model.config.id2label[class_id.item()]
        confidence_score = confidence.item()
        
        # Apply neutral threshold for low confidence
        if confidence_score < 0.60:  # Confidence threshold for neutral
            sentiment_labels.append(('NEUTRAL', confidence_score))
        else:
            sentiment_labels.append((sentiment.upper(), confidence_score))
    
    return sentiment_labels

def analyze_reviews(df, text_column='review', batch_size=32):
    """
    Perform sentiment analysis on all reviews in the dataframe
    """
    
    # Load model and tokenizer
    tokenizer, model, labels = load_model_and_tokenizer()
    
    # Get all reviews
    reviews = df[text_column].fillna('').tolist()
    
    print(f"\n Analyzing {len(reviews)} reviews...")
    
    # Process in batches
    all_results = []
    
    for i in range(0, len(reviews), batch_size):
        batch_reviews = reviews[i:i+batch_size]
        batch_results = predict_sentiment_batch(batch_reviews, tokenizer, model, batch_size)
        all_results.extend(batch_results)
    
    # Add results to dataframe
    df['sentiment_label'] = [r[0] for r in all_results]
    df['sentiment_score'] = [r[1] for r in all_results]
    
    return df

def main():
    """
    Main execution function
    """
    print("="*60)
    print(" DISTILBERT SENTIMENT ANALYSIS")
    print("="*60)
    
    # Load your cleaned reviews
    df = pd.read_csv('data/cleaned_reviews.csv')
    print(f" Loaded {len(df)} reviews")
    
    # Perform sentiment analysis
    df = analyze_reviews(df)
    
    # Display results summary
    print("\n" + "="*60)
    print(" SENTIMENT ANALYSIS RESULTS")
    print("="*60)
    
    print("\nOverall Sentiment Distribution:")
    sentiment_counts = df['sentiment_label'].value_counts()
    for sentiment, count in sentiment_counts.items():
        pct = (count / len(df)) * 100
        print(f"   {sentiment}: {count} ({pct:.1f}%)")
    
    print("\nSentiment by Bank:")
    for bank in df['bank'].unique():
        bank_df = df[df['bank'] == bank]
        print(f"\n   {bank}:")
        for sentiment in ['POSITIVE', 'NEUTRAL', 'NEGATIVE']:
            count = len(bank_df[bank_df['sentiment_label'] == sentiment])
            pct = (count / len(bank_df)) * 100
            print(f"      {sentiment}: {count} ({pct:.1f}%)")
    
    # Save results
    output_path = 'data/sentiment_results_distilbert.csv'
    df.to_csv(output_path, index=False)
    print(f"\n Results saved to: {output_path}")
    
    return df

if __name__ == "__main__":
    sentiment_df = main()