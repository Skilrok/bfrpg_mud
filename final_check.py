from app.database import get_db
from app.models import Character, User, CharacterItem

def check_database():
    print("Checking database integrity...")
    
    db = next(get_db())
    
    # Check characters
    try:
        character_count = db.query(Character).count()
        print(f"Total characters: {character_count}")
        
        # Check character details
        characters = db.query(Character).all()
        print("\nCharacter details:")
        for char in characters:
            print(f"ID: {char.id}, Name: {char.name}, Race: {char.race}, Class: {char.character_class}")
            print(f"  Owner/User ID: {char.user_id}")
            if char.user:
                print(f"  Owner Username: {char.user.username}")
            
            # Check if owner property works
            assert char.owner is char.user, "Owner property doesn't match user property"
        
        # Check character items
        item_count = db.query(CharacterItem).count()
        print(f"\nTotal character items: {item_count}")
        
        print("\nDatabase integrity check completed successfully!")
        
    except Exception as e:
        print(f"Error during database check: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database() 