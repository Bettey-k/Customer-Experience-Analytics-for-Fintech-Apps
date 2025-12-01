import os

import psycopg2
from dotenv import load_dotenv
import pandas as pd

def get_db_connection():
    load_dotenv()
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "bank_reviews"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )

def verify_data():
    conn = get_db_connection()
    
    try:
        # Query 1: Count of reviews per bank
        query1 = """
        SELECT b.bank_name, COUNT(r.review_id) as review_count
        FROM banks b
        LEFT JOIN reviews r ON b.bank_id = r.bank_id
        GROUP BY b.bank_name
        ORDER BY review_count DESC
        """
        
        # Query 2: Average rating by bank
        query2 = """
        SELECT b.bank_name, 
               ROUND(AVG(r.rating), 2) as avg_rating,
               COUNT(r.review_id) as review_count
        FROM banks b
        LEFT JOIN reviews r ON b.bank_id = r.bank_id
        GROUP BY b.bank_name
        ORDER BY avg_rating DESC
        """
        
        # Query 3: Sentiment distribution
        query3 = """
        SELECT b.bank_name, 
               r.sentiment_label,
               COUNT(*) as count,
               ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY b.bank_name), 2) as percentage
        FROM reviews r
        JOIN banks b ON r.bank_id = b.bank_id
        GROUP BY b.bank_name, r.sentiment_label
        ORDER BY b.bank_name, count DESC
        """
        
        # Execute and display results
        print("\n=== Reviews per Bank ===")
        df1 = pd.read_sql(query1, conn)
        print(df1.to_string(index=False))
        
        print("\n=== Average Rating by Bank ===")
        df2 = pd.read_sql(query2, conn)
        print(df2.to_string(index=False))
        
        print("\n=== Sentiment Distribution ===")
        df3 = pd.read_sql(query3, conn)
        print(df3.to_string(index=False))
        
    except Exception as e:
        print(f"Error verifying data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_data()