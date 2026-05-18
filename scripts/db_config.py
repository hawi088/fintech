import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'bank_reviews'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD')
    }