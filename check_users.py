import os
import sqlite3
import sys
from pathlib import Path


def check_database_users(db_file):
    """Check available users in the database"""
    try:
        # Find the database file
        db_path = Path(db_file)
        if not db_path.exists():
            print(f"Database file not found at {db_path.absolute()}")
            return False

        print(f"Found database at {db_path.absolute()}")

        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if users table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        if not cursor.fetchone():
            print("No 'users' table found in the database")

            # List all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Available tables: {[t[0] for t in tables]}")
            return False

        # Get user count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"Found {user_count} users in the database")

        # Get user data
        cursor.execute(
            "SELECT id, username, email, is_admin, is_active, hashed_password FROM users"
        )
        users = cursor.fetchall()

        print("\n=== USERS IN DATABASE ===")
        print(
            f"{'ID':^5} | {'Username':^20} | {'Email':^30} | {'Admin':^5} | {'Active':^6} | {'Password Hash Preview':^20}"
        )
        print("-" * 100)

        for user in users:
            user_id, username, email, is_admin, is_active, hashed_pwd = user
            pwd_preview = hashed_pwd[:10] + "..." if hashed_pwd else "None"
            print(
                f"{user_id:^5} | {username:^20} | {email:^30} | {is_admin:^5} | {is_active:^6} | {pwd_preview:^20}"
            )

        # Close the connection
        conn.close()
        return True

    except Exception as e:
        print(f"Error checking database {db_file}: {e}")
        import traceback

        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    print("Database User Check")
    print("==================\n")

    # Try both known database files
    database_files = ["bfrpg.db", "dev.db"]

    for db_file in database_files:
        print(f"\nChecking database: {db_file}")
        print("-" * 30)
        check_database_users(db_file)
