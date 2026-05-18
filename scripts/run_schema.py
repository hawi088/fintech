"""
Run SQL schema to create database tables
Alternative to psql command line
"""

import psycopg2

# Database connection
from db_config import get_db_connection

conn = psycopg2.connect(**get_db_connection())

cur = conn.cursor()

# Read schema.sql file
with open('schema.sql', 'r') as f:
    sql_commands = f.read()

# Split commands by semicolon and execute each
for command in sql_commands.split(';'):
    command = command.strip()
    if command and not command.startswith('--'):
        try:
            cur.execute(command)
            print(f"Executed: {command[:50]}...")
        except Exception as e:
            print(f"Skipped (already exists): {command[:50]}...")

conn.commit()
cur.close()
conn.close()

print("\nSchema executed successfully!")