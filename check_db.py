import sqlite3
import os

def check_db(db_path):
    print(f"Checking database: {db_path}")
    print(f"Database exists: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {[table[0] for table in tables]}")
        
        # Check if users table exists and its structure
        if any(table[0] == 'users' for table in tables):
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print(f"User table columns: {[col[1] for col in columns]}")
            
            # Check if there are any users
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"User count: {user_count}")
            
            if user_count > 0:
                # Get usernames
                cursor.execute("SELECT id, username, email FROM users")
                users = cursor.fetchall()
                print(f"Users: {users}")
        
        conn.close()
    except Exception as e:
        print(f"Error checking database: {str(e)}")

if __name__ == "__main__":
    print("Script to check database status")
    check_db("dev.db")
    check_db("test.db")
    check_db("sqlite.db")
    check_db("bfrpg.db") 