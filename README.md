# Fintech Review Analytics

## Project Overview

Analyzing Google Play Store reviews for Ethiopian banks (CBE, BOA, Dashen) to extract sentiment and themes. This project helps banks understand what users love, what frustrates them, and what to prioritize next.

### Business Problem

Mobile banking adoption in Ethiopia is accelerating. Thousands of users leave reviews daily, but this feedback remains unanalyzed. This project transforms raw reviews into actionable insights for product teams.

### Objectives

- Scrape and clean user reviews from Google Play Store
- Classify sentiment (positive/negative/neutral)
- Extract recurring themes (login issues, transfer problems, UI complaints)
- Provide bank-specific recommendations

---

## Data Collection Methodology

### Scraping Strategy

Reviews were scraped from the Google Play Store using the `google-play-scraper` Python library. The following apps were targeted:

| Bank | App Name | Package Name |
|------|----------|--------------|
| CBE | Commercial Bank of Ethiopia | `com.combanketh.mobilebanking` |
| BOA | Bank of Abyssinia | `com.boa.boaMobileBanking` |
| Dashen | Dashen Bank | `com.dashen.dashensuperapp` |

### Scraping Parameters

| Parameter | Value |
|-----------|-------|
| Language | English (`lang='en'`) |
| Country | United States (`country='us'`) |
| Sort Order | Newest first (`Sort.NEWEST`) |
| Target per bank | 500+ reviews |

### Data Collection Results

| Bank | Reviews Collected | Status |
|------|------------------|--------|
| CBE | 500 |  Success |
| BOA | 500 |  Success |
| Dashen | 500 |  Success |
| **Total** | **1,500** |  |

### Date Range

The collected reviews span from **February 12, 2025** to **May 14, 2026** (approximately 15 months).

### Scraping Limitations

1. **Rate Limiting:** Google Play enforces rate limits. A 1-2 second delay was added between requests to avoid being blocked.
2. **Review Availability:** Only reviews with written text were collected. Pure star ratings without comments are not included.
3. **Language Filter:** Only English reviews were collected due to the scope of this analysis.
4. **Pagination:** The continuation token method was used to fetch all available reviews, which successfully retrieved 500 reviews per bank.

### Data Preprocessing

After scraping, the following cleaning steps were applied:

1. **Duplicate Removal:** 0 duplicate reviews found and removed
2. **Missing Values:** 0 rows with missing review text or rating
3. **Date Normalization:** Converted all dates to `YYYY-MM-DD` format
4. **Final Dataset Columns:** `review`, `rating`, `date`, `bank`, `source`

### Final Dataset Quality

| Metric | Value |
|--------|-------|
| Total reviews | 1,500 |
| Reviews with text | 1,500 (100%) |
| Complete ratings | 1,500 (100%) |
| Date range | 2025-02-12 to 2026-05-14 |

### Rating Distribution

| Rating | Count | Percentage |
|--------|-------|------------|
| 5 stars | 939 | 62.6% |
| 4 stars | 111 | 7.4% |
| 3 stars | 80 | 5.3% |
| 2 stars | 48 | 3.2% |
| 1 star | 322 | 21.5% |

---

## Setup Instructions

### Prerequisites

- Python 3.9+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/hawi088/fintech.git
cd fintech
```