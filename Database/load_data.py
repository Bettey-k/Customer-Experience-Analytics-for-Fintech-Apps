import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "bank_reviews"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )


def insert_bank_data(conn, bank_name, app_name=None):
    """Insert bank data and return the bank_id"""
    with conn.cursor() as cur:
        # Check if bank exists
        cur.execute("SELECT bank_id FROM banks WHERE bank_name = %s", (bank_name,))
        result = cur.fetchone()
        
        if result:
            return result[0]
        
        # Insert new bank
        cur.execute(
            "INSERT INTO banks (bank_name, app_name) VALUES (%s, %s) RETURNING bank_id",
            (bank_name, app_name or bank_name)
        )
        bank_id = cur.fetchone()[0]
        conn.commit()
        return bank_id

def insert_review_data(conn, bank_id, review_data):
    """Insert review data into the database"""
    with conn.cursor() as cur:
        # Convert themes list to PostgreSQL array format
        themes = review_data.get('themes', [])
        if isinstance(themes, str):
            themes = [themes]
        
        # Prepare the insert query
        query = """
        INSERT INTO reviews (
            bank_id, review_text, rating, review_date, 
            sentiment_label, sentiment_score, source, language, themes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (
            bank_id,
            review_data.get('review'),
            review_data.get('rating'),
            review_data.get('date'),
            review_data.get('sentiment'),
            review_data.get('sentiment_score'),
            review_data.get('source', 'unknown'),
            review_data.get('language', 'en'),
            themes
        ))
        conn.commit()

def main():
    # Load your cleaned data
    df = pd.read_csv('data/analyzed_reviews_20251129_215241.csv')
    
    # Connect to the database
    conn = get_db_connection()
    
    try:
        # Process each unique bank
        for bank_name in df['bank'].unique():
            print(f"Processing bank: {bank_name}")
            
            # Insert bank and get bank_id
            bank_id = insert_bank_data(conn, bank_name)
            
            # Insert reviews for this bank
            bank_reviews = df[df['bank'] == bank_name]
            for _, review in bank_reviews.iterrows():
                try:
                    insert_review_data(conn, bank_id, review.to_dict())
                except Exception as e:
                    print(f"Error inserting review: {e}")
                    conn.rollback()
                    continue
        
        print("Data loading completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()