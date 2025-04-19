import sqlite3
import datetime
from app.routers.auth import get_password_hash

def add_admin_column():
    print("Adding is_admin column to users table in dev.db")
    
    try:
        # Connect to the database
        conn = sqlite3.connect("dev.db")
        cursor = conn.cursor()
        
        # Check if the is_admin column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if "is_admin" not in column_names:
            print("Adding is_admin column...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
            conn.commit()
            print("is_admin column added successfully")
        else:
            print("is_admin column already exists")
        
        # Create admin user if it doesn't exist
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        now = datetime.datetime.utcnow().isoformat()
        
        if not admin_user:
            print("Creating admin user...")
            hashed_password = get_password_hash("admin")
            cursor.execute(
                "INSERT INTO users (username, email, hashed_password, is_active, is_admin, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("admin", "admin@example.com", hashed_password, True, True, now, now)
            )
            conn.commit()
            print("Admin user created successfully")
        else:
            print("Admin user already exists")
            # Update existing admin user to have admin privileges
            cursor.execute("UPDATE users SET is_admin = ? WHERE username = ?", (True, "admin"))
            conn.commit()
            print("Updated existing admin user with admin privileges")
        
        # Verify admin user exists
        cursor.execute("SELECT id, username, email, is_admin FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        print(f"Admin user: {admin_user}")
        
        conn.close()
        print("Database operation completed successfully")
        
    except Exception as e:
        print(f"Error updating database: {str(e)}")

if __name__ == "__main__":
    add_admin_column() 