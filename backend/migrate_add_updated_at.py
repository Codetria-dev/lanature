"""
Migration script to add updated_at column to users table.

This script safely adds the updated_at column if it doesn't exist.
Run this once to fix the database schema mismatch.
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for development by default, PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lanature.db")

# SQLite needs check_same_thread=False
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

def migrate():
    """Add updated_at column to users table if it doesn't exist."""
    with engine.connect() as conn:
        # Check if column exists (SQLite specific)
        if DATABASE_URL.startswith("sqlite"):
            # SQLite doesn't support IF NOT EXISTS for ALTER TABLE ADD COLUMN
            # So we check if column exists first
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('users') 
                WHERE name='updated_at'
            """))
            column_exists = result.fetchone()[0] > 0
            
            if not column_exists:
                print("Adding updated_at column to users table...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN updated_at DATETIME
                """))
                conn.commit()
                print("[OK] Successfully added updated_at column to users table")
            else:
                print("[OK] updated_at column already exists in users table")
        else:
            # PostgreSQL
            print("Adding updated_at column to users table (PostgreSQL)...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE
            """))
            conn.commit()
            print("[OK] Successfully added updated_at column to users table")
    
    print("Migration completed!")

if __name__ == "__main__":
    migrate()
