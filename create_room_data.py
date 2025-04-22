import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database path
DB_PATH = "./bfrpg.db"

def create_rooms_and_exits():
    """Create rooms and exits"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if rooms table exists
        cursor.execute("SELECT COUNT(*) FROM rooms")
        room_count = cursor.fetchone()[0]
        logger.info(f"Existing room count: {room_count}")
        
        # Check if any rooms exist
        if room_count < 5:
            # Add remaining rooms if only the first room exists
            if room_count == 1:
                logger.info("Adding remaining rooms")
                
                # Tavern (Room 2)
                cursor.execute("""
                    INSERT INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark) 
                    VALUES (2, 'Village Tavern', 'A cozy tavern with a roaring fireplace. Adventurers gather here to share tales and find work. The bartender nods at you as you enter.', 'town', 1, 0, 1, 0, 0)
                """)
                
                # Market (Room 3)
                cursor.execute("""
                    INSERT INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark) 
                    VALUES (3, 'Village Market', 'A bustling market with various stalls selling goods. Merchants call out to passersby, hawking their wares.', 'town', 1, 1, 0, 0, 0)
                """)
                
                # Blacksmith (Room 4)
                cursor.execute("""
                    INSERT INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark) 
                    VALUES (4, 'Village Blacksmith', 'The sound of hammering fills the air as the blacksmith works at the forge. Weapons and armor are displayed on the walls.', 'town', 1, 0, -1, 0, 0)
                """)
                
                # Temple (Room 5)
                cursor.execute("""
                    INSERT INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark) 
                    VALUES (5, 'Village Temple', 'A peaceful temple dedicated to various deities. Candles flicker in the dim interior, and a priest stands ready to offer healing and blessings.', 'town', 1, -1, 0, 0, 0)
                """)
            
        # Check if exits table exists
        cursor.execute("SELECT COUNT(*) FROM exits")
        exit_count = cursor.fetchone()[0]
        logger.info(f"Existing exit count: {exit_count}")
        
        # Add exits if none exist
        if exit_count == 0:
            logger.info("Adding exits")
            
            # From Village Square (Room 1) to other rooms
            cursor.execute("""
                INSERT INTO exits (direction, name, description, source_room_id, destination_room_id)
                VALUES ('north', 'Tavern Entrance', 'The door to the village tavern.', 1, 2)
            """)
            
            cursor.execute("""
                INSERT INTO exits (direction, name, description, source_room_id, destination_room_id)
                VALUES ('east', 'Market Street', 'A path leading to the village market.', 1, 3)
            """)
            
            cursor.execute("""
                INSERT INTO exits (direction, name, description, source_room_id, destination_room_id)
                VALUES ('south', 'Smithy Road', 'A path leading to the village blacksmith.', 1, 4)
            """)
            
            cursor.execute("""
                INSERT INTO exits (direction, name, description, source_room_id, destination_room_id)
                VALUES ('west', 'Temple Path', 'A serene path leading to the village temple.', 1, 5)
            """)
            
            # Return paths back to Village Square (Room 1)
            cursor.execute("""
                INSERT INTO exits (direction, name, description, source_room_id, destination_room_id)
                VALUES ('south', 'Exit to Village Square', 'The door leading back to the village square.', 2, 1)
            """)
            
            cursor.execute("""
                INSERT INTO exits (direction, name, description, source_room_id, destination_room_id)
                VALUES ('west', 'Back to Village Square', 'The path leading back to the village square.', 3, 1)
            """)
            
            cursor.execute("""
                INSERT INTO exits (direction, name, description, source_room_id, destination_room_id)
                VALUES ('north', 'Back to Village Square', 'The path leading back to the village square.', 4, 1)
            """)
            
            cursor.execute("""
                INSERT INTO exits (direction, name, description, source_room_id, destination_room_id)
                VALUES ('east', 'Back to Village Square', 'The path leading back to the village square.', 5, 1)
            """)
            
        # Commit changes
        conn.commit()
        
        # Check final counts
        cursor.execute("SELECT COUNT(*) FROM rooms")
        final_room_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM exits")
        final_exit_count = cursor.fetchone()[0]
        
        logger.info(f"Final room count: {final_room_count}")
        logger.info(f"Final exit count: {final_exit_count}")
        
        # List the rooms
        logger.info("Rooms in database:")
        cursor.execute("SELECT id, name FROM rooms")
        for room in cursor.fetchall():
            logger.info(f"  Room {room[0]}: {room[1]}")
            
        # List the exits
        logger.info("Exits in database:")
        cursor.execute("SELECT source_room_id, direction, destination_room_id FROM exits")
        for exit_data in cursor.fetchall():
            logger.info(f"  From Room {exit_data[0]} {exit_data[1]} to Room {exit_data[2]}")
        
        return True
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {str(e)}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info("Creating rooms and exits...")
    result = create_rooms_and_exits()
    logger.info(f"Creation {'successful' if result else 'failed'}") 