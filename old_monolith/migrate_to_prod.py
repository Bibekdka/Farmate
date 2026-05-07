import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables but specifically grab the Render DB URL
# The .env currently has it commented out, so we'll hardcode it just for the script based on .env content
load_dotenv()

SQLITE_URL = 'sqlite:///instance/farm_data.db'
# This is the Render URL from your .env
POSTGRES_URL = 'postgresql+psycopg://farm_db_myec_user:hM3S5wGB5goEbmjqQV9c7dA9R4Y68Xxj@dpg-d7te7irrjlhs73apot60-a.virginia-postgres.render.com/farm_db_myec'

def migrate_data():
    print("Connecting to local SQLite database...")
    sqlite_engine = create_engine(SQLITE_URL)
    
    print("Connecting to remote PostgreSQL database on Render...")
    print("This might take a moment...")
    pg_engine = create_engine(POSTGRES_URL)
    
    # List of all tables in the database
    tables = [
        'user', 'product', 'farm_record', 'note', 'crop', 'yield', 
        'disease_log', 'pest_log', 'reminder', 'weather_log', 'order', 'visit'
    ]
    
    for table in tables:
        try:
            print(f"Reading local data from table '{table}'...")
            df = pd.read_sql_table(table, sqlite_engine)
            
            if len(df) > 0:
                print(f"Uploading {len(df)} rows to remote table '{table}'...")
                
                # Clear the remote table first to avoid duplicate key errors
                from sqlalchemy import text
                with pg_engine.begin() as conn:
                    conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                    
                df.to_sql(table, pg_engine, if_exists='append', index=False)
                print(f"Successfully migrated {table}!")
            else:
                print(f"Table '{table}' is empty locally, skipping.")
        except Exception as e:
            print(f"Could not migrate table '{table}' - see error.txt")
            with open("error.txt", "a", encoding="utf-8") as f:
                f.write(f"Could not migrate table '{table}': {str(e)}\n")
            
    print("\nMIGRATION COMPLETE! Your local data is now live on Render.")

if __name__ == '__main__':
    print("="*50)
    print("LOCAL TO RENDER CLOUD DATA MIGRATION SCRIPT")
    print("="*50)
    migrate_data()
