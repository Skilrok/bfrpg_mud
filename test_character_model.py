from app.models import Character, User
from app.database import get_db

def test_character_model():
    print("Testing Character model...")
    
    # Test importing the model
    print("Character model imported successfully")
    
    # Test the owner property
    try:
        # Get the first character
        db = next(get_db())
        character = db.query(Character).first()
        
        if character:
            print(f"Found character: {character.name}")
            
            # Test the user relationship
            print(f"Character user: {character.user}")
            
            # Test the owner property
            print(f"Character owner: {character.owner}")
            
            # Verify they are the same object
            print(f"user is owner: {character.user is character.owner}")
            
            print("Owner property works correctly!")
        else:
            print("No characters found in the database")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_character_model() 