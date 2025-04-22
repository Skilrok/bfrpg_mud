import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database path
DB_PATH = "./bfrpg.db"

def create_missing_tables():
    """Create missing tables needed by the look command"""
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create items table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                item_type TEXT,
                weight REAL DEFAULT 0,
                value INTEGER DEFAULT 0,
                properties TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Created items table if it didn't exist")
        
        # Create room_items table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS room_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL REFERENCES rooms(id),
                item_id INTEGER NOT NULL REFERENCES items(id),
                quantity INTEGER DEFAULT 1,
                properties TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Created room_items table if it didn't exist")
        
        # Create npcs table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS npcs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                level INTEGER DEFAULT 1,
                health INTEGER DEFAULT 10,
                properties TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Created npcs table if it didn't exist")
        
        # Create room_npcs table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS room_npcs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL REFERENCES rooms(id),
                npc_id INTEGER NOT NULL REFERENCES npcs(id),
                properties TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Created room_npcs table if it didn't exist")
        
        # Check if characters table is needed
        try:
            cursor.execute("SELECT 1 FROM characters LIMIT 1")
            cursor.fetchone()
            logger.info("Characters table already exists")
        except sqlite3.OperationalError:
            # Create characters table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    level INTEGER DEFAULT 1,
                    user_id INTEGER REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Created characters table if it didn't exist")
            
            # Add a test character if one doesn't exist
            cursor.execute("SELECT id FROM characters WHERE id = 1")
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO characters (id, name, description, level, user_id)
                    VALUES (1, 'Bob', 'A test character', 1, 1)
                """)
                logger.info("Added test character 'Bob'")
                
                # Make sure Bob has a location
                cursor.execute("SELECT 1 FROM character_locations WHERE character_id = 1")
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO character_locations (character_id, room_id)
                        VALUES (1, 1)
                    """)
                    logger.info("Added location for test character")
        
        conn.commit()
        logger.info("Successfully created missing tables")
        
        # Add some example data to make the look command more interesting
        # Add a tavern keeper NPC
        cursor.execute("""
            INSERT OR IGNORE INTO npcs (id, name, description)
            VALUES (1, 'Tavern Keeper', 'A friendly barkeeper with a jovial smile.')
        """)
        
        # Place the tavern keeper in the tavern
        cursor.execute("""
            INSERT OR IGNORE INTO room_npcs (room_id, npc_id)
            VALUES (2, 1)
        """)
        
        # Add a sword item
        cursor.execute("""
            INSERT OR IGNORE INTO items (id, name, description, item_type, value)
            VALUES (1, 'Longsword', 'A well-crafted steel sword.', 'weapon', 15)
        """)
        
        # Place the sword in the blacksmith
        cursor.execute("""
            INSERT OR IGNORE INTO room_items (room_id, item_id, quantity)
            VALUES (4, 1, 1)
        """)
        
        conn.commit()
        logger.info("Successfully added example NPCs and items")
        
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info("Creating missing tables...")
    success = create_missing_tables()
    logger.info(f"Table creation {'successful' if success else 'failed'}") 