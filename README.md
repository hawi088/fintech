## Task 3: PostgreSQL Database Setup

### Database Architecture

A PostgreSQL database named `bank_reviews` was designed to store and query the analyzed review data. The schema follows a star schema pattern with two tables: `banks` (dimension) and `reviews` (fact).

#### Schema Design

**Banks Table (Dimension)**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| bank_id | SERIAL | PRIMARY KEY | Unique identifier for each bank |
| bank_name | VARCHAR(50) | NOT NULL, UNIQUE | Bank name (CBE, BOA, Dashen) |
| app_name | VARCHAR(100) | | Full mobile application name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Reviews Table (Fact)**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| review_id | VARCHAR(100) | PRIMARY KEY | Unique review identifier |
| bank_id | INTEGER | FOREIGN KEY (banks) | Links review to specific bank |
| review_text | TEXT | NOT NULL | Original user review content |
| rating | INTEGER | CHECK (1-5) | Star rating (1 to 5) |
| review_date | DATE | | Date when review was posted |
| sentiment_label | VARCHAR(10) | | POSITIVE, NEGATIVE, or NEUTRAL |
| sentiment_score | DECIMAL(5,4) | | Confidence score from 0 to 1 |
| identified_theme | VARCHAR(100) | | Extracted theme category |
| source | VARCHAR(50) | | Data source (Google Play) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### Setup Instructions

#### Step 1: Install PostgreSQL

Download and install PostgreSQL from https://www.postgresql.org/download/

Default installation includes:
- PostgreSQL server
- pgAdmin (GUI management tool)
- Command line tools (psql)

#### Step 2: Create Database

Using pgAdmin:
1. Open pgAdmin
2. Right-click on "Databases" -> Create -> Database
3. Name: `bank_reviews`
4. Click Save

Using command line:
```bash
psql -U postgres -c "CREATE DATABASE bank_reviews;"
```
#### Step 3: Run Schema
Execute the schema file to create tables and indexes:

```bash
psql -U postgres -d bank_reviews -f schema.sql
```
#### Step 4: Configure Database Connection
```bash
DB_HOST=localhost
DB_NAME=bank_reviews
DB_USER=postgres
DB_PASSWORD=your_password_here
```
##### Step 5: Install Python Dependencies
```bash
pip install psycopg2-binary pandas python-dotenv
```

