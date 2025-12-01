import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    # Connect to the default 'postgres' database to create other databases
    conn = psycopg2.connect(
        dbname="postgres",
        user=os.getenv("DB_USER", "postgres"),   # FIXED
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
        # No password needed for your setup
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'bank_reviews'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE bank_reviews")
            print("Database 'bank_reviews' created successfully")
        else:
            print("Database 'bank_reviews' already exists")
            
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()
        conn.close()

def create_tables():
    # Connect specifically to bank_reviews DB
    conn = psycopg2.connect(
        dbname="bank_reviews",
        user=os.getenv("DB_USER", "postgres"),   # FIXED
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
        # No password needed
    )
    cursor = conn.cursor()
    
    # SQL commands to create tables
    commands = (
        """
        CREATE TABLE IF NOT EXISTS banks (
            bank_id SERIAL PRIMARY KEY,
            bank_name VARCHAR(100) NOT NULL,
            app_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS reviews (
            review_id SERIAL PRIMARY KEY,
            bank_id INTEGER REFERENCES banks(bank_id),
            review_text TEXT,
            rating INTEGER,
            review_date DATE,
            sentiment_label VARCHAR(20),
            sentiment_score FLOAT,
            source VARCHAR(100),
            language VARCHAR(10),
            themes TEXT[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    
    try:
        for command in commands:
            cursor.execute(command)
        conn.commit()
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_database()
    create_tables()
