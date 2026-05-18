-- ============================================
-- Database Schema for Bank Reviews Analytics
-- Database: bank_reviews
-- ============================================

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS banks CASCADE;

-- ============================================
-- Table: banks
-- Stores metadata about each bank
-- ============================================
CREATE TABLE banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(50) NOT NULL UNIQUE,
    app_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Table: reviews
-- Stores scraped and processed review data
-- ============================================
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
);

-- ============================================
-- Insert bank data
-- ============================================
INSERT INTO banks (bank_name, app_name) VALUES 
('CBE', 'Commercial Bank of Ethiopia Mobile'),
('BOA', 'Bank of Abyssinia Mobile'),
('Dashen', 'Dashen Bank Super App')
ON CONFLICT (bank_name) DO NOTHING;

-- ============================================
-- Verification Queries
-- ============================================

-- Count reviews per bank
SELECT b.bank_name, COUNT(r.review_id) as review_count
FROM banks b
LEFT JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_name
ORDER BY b.bank_name;

-- Average rating per bank (where rating exists)
SELECT b.bank_name, ROUND(AVG(r.rating), 2) as avg_rating
FROM banks b
JOIN reviews r ON b.bank_id = r.bank_id
WHERE r.rating IS NOT NULL
GROUP BY b.bank_name
ORDER BY avg_rating DESC;

-- Sentiment distribution
SELECT sentiment_label, COUNT(*) as count
FROM reviews
GROUP BY sentiment_label
ORDER BY count DESC;

-- Theme distribution
SELECT identified_theme, COUNT(*) as count
FROM reviews
GROUP BY identified_theme
ORDER BY count DESC
LIMIT 5;

-- Null check in key columns
SELECT 
    COUNT(*) as total_reviews,
    SUM(CASE WHEN review_text IS NULL THEN 1 ELSE 0 END) as null_review_text,
    SUM(CASE WHEN sentiment_label IS NULL THEN 1 ELSE 0 END) as null_sentiment,
    SUM(CASE WHEN bank_id IS NULL THEN 1 ELSE 0 END) as null_bank_id
FROM reviews;