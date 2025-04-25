from app.database import get_db_context
from sqlalchemy.sql import text
from app.models import CharacterRace

def fix_character_race():
    """Fix case sensitivity issues in character race enum columns"""
    print("Fixing character race enum values")

    with get_db_context() as db:
        # Get all characters
        results = db.execute(text("SELECT id, name, race FROM characters")).fetchall()
        
        # Direct SQL updates for each race type
        db.execute(text("UPDATE characters SET race = 'HUMAN' WHERE LOWER(race) = 'human'"))
        db.execute(text("UPDATE characters SET race = 'DWARF' WHERE LOWER(race) = 'dwarf'"))
        db.execute(text("UPDATE characters SET race = 'ELF' WHERE LOWER(race) = 'elf'"))
        db.execute(text("UPDATE characters SET race = 'HALFLING' WHERE LOWER(race) = 'halfling'"))
        
        # Commit changes
        db.commit()
        
        # Verify changes
        print("\nVerifying changes:")
        results = db.execute(text("SELECT id, name, race FROM characters")).fetchall()
        for row in results:
            char_id, name, race = row
            print(f"Character {name} (ID: {char_id}) has race: {race}")
            
        print("Done fixing character races")

if __name__ == "__main__":
    fix_character_race() 