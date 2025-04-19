"""
Create Starter Area Script

This script sets up the initial game area, including:
1. A "Starting Village" area
2. Multiple rooms in the village
3. Exits connecting the rooms
4. A few basic items in the rooms

Run this script to initialize a basic game world for testing
"""

import asyncio
import os
import sys
import logging

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db_context, init_db
from app.models.room import Area, Room, RoomType
from app.models.exit import Exit 
from app.models.item import Item

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Room descriptions
VILLAGE_SQUARE_DESC = """
A bustling village square forms the heart of this small settlement. A stone fountain 
stands in the center, its waters catching the sunlight. Villagers go about their 
daily business while merchants hawk their wares from small stalls along the edges 
of the square. The air smells of fresh bread and woodsmoke.
""".strip()

BLACKSMITH_DESC = """
The blacksmith's forge radiates heat as the smith pounds glowing metal on an anvil. 
Sparks fly with each strike of the hammer. Weapons and tools of various types hang 
on the walls, and a barrel of water steams when hot metal is plunged into it. The 
smell of coal and hot metal fills the air.
""".strip()

TAVERN_DESC = """
The Laughing Dragon Tavern is warm and inviting. A fire crackles in a stone hearth, 
casting dancing shadows on the wooden walls. Patrons sit at rough-hewn tables, sharing 
stories over mugs of ale. A bard plays a lively tune in the corner, nearly drowned out 
by the sounds of conversation and laughter.
""".strip()

GENERAL_STORE_DESC = """
Shelves line the walls of this cluttered shop, filled with goods of all kinds. Ropes, 
tools, lanterns, and dried foods are stacked in neat piles. The shopkeeper, an elderly 
halfling, sits behind a counter, carefully counting coins. A bell above the door jingles 
as customers enter and exit.
""".strip()

VILLAGE_PATH_DESC = """
A well-worn dirt path winds between the humble buildings of the village. Chickens 
scratch in the dirt, and the occasional cat lounges in patches of sunlight. The sounds 
of village life - children playing, people working, animals calling - create a peaceful 
ambiance.
""".strip()

VILLAGE_GATE_DESC = """
A simple wooden gate marks the entrance to the village. It stands open during the day, 
flanked by two wooden posts carved with protective symbols. Beyond the gate, a road 
leads into the wilderness, promising adventure and danger in equal measure.
""".strip()

FOREST_EDGE_DESC = """
The cultivated land of the village gives way to wild forest here. Ancient trees stand 
like sentinels at the edge of civilization, their branches swaying in the breeze. 
A narrow trail disappears into the shadows beneath the canopy, and strange sounds 
echo from the depths of the woods.
""".strip()


async def create_starter_area():
    """Create a basic starter area with connected rooms"""
    try:
        await init_db()  # Make sure the database is initialized
        
        with get_db_context() as db:
            logger.info("Creating starter area...")
            
            # Check if starter area already exists
            existing_area = db.query(Area).filter(Area.name == "Starting Village").first()
            if existing_area:
                logger.info("Starter area already exists. Skipping creation.")
                return
            
            # Create the area
            area = Area(
                name="Starting Village",
                description="A peaceful village nestled between rolling hills and a dense forest. This is where new adventurers begin their journey.",
                level_range="1-3",
                is_dungeon=False,
                is_hidden=False,
                properties={
                    "is_safe": True,
                    "respawn_point": True,
                    "background_music": "village_theme.mp3"
                }
            )
            db.add(area)
            db.flush()  # Get the area ID
            
            logger.info(f"Created area: {area.name} (ID: {area.id})")
            
            # Create rooms
            rooms = {
                "village_square": Room(
                    name="Village Square",
                    description=VILLAGE_SQUARE_DESC,
                    room_type=RoomType.TOWN,
                    area_id=area.id,
                    coordinates={"x": 0, "y": 0, "z": 0},
                    properties={"is_spawn_point": True}
                ),
                "blacksmith": Room(
                    name="Blacksmith's Forge",
                    description=BLACKSMITH_DESC,
                    room_type=RoomType.BUILDING,
                    area_id=area.id,
                    coordinates={"x": 1, "y": 0, "z": 0}
                ),
                "tavern": Room(
                    name="The Laughing Dragon Tavern",
                    description=TAVERN_DESC,
                    room_type=RoomType.BUILDING,
                    area_id=area.id,
                    coordinates={"x": -1, "y": 0, "z": 0}
                ),
                "general_store": Room(
                    name="General Store",
                    description=GENERAL_STORE_DESC,
                    room_type=RoomType.BUILDING,
                    area_id=area.id,
                    coordinates={"x": 0, "y": 1, "z": 0}
                ),
                "north_path": Room(
                    name="North Village Path",
                    description=VILLAGE_PATH_DESC,
                    room_type=RoomType.TOWN,
                    area_id=area.id,
                    coordinates={"x": 0, "y": 2, "z": 0}
                ),
                "village_gate": Room(
                    name="Village Gate",
                    description=VILLAGE_GATE_DESC,
                    room_type=RoomType.TOWN,
                    area_id=area.id,
                    coordinates={"x": 0, "y": 3, "z": 0}
                ),
                "forest_edge": Room(
                    name="Edge of the Forest",
                    description=FOREST_EDGE_DESC,
                    room_type=RoomType.FOREST,
                    area_id=area.id,
                    coordinates={"x": 0, "y": 4, "z": 0}
                )
            }
            
            # Add all rooms to the database
            for key, room in rooms.items():
                db.add(room)
            
            db.flush()  # Generate IDs for the rooms
            
            logger.info(f"Created {len(rooms)} rooms")
            
            # Create exits between rooms
            exits = [
                # Village Square to other buildings
                Exit(
                    source_room_id=rooms["village_square"].id,
                    destination_room_id=rooms["blacksmith"].id,
                    direction="east",
                    name="blacksmith's forge",
                    description="The sound of hammering draws you toward the blacksmith's forge."
                ),
                Exit(
                    source_room_id=rooms["blacksmith"].id,
                    destination_room_id=rooms["village_square"].id,
                    direction="west",
                    name="village square",
                    description="The doorway leads back to the village square."
                ),
                
                Exit(
                    source_room_id=rooms["village_square"].id,
                    destination_room_id=rooms["tavern"].id,
                    direction="west",
                    name="tavern door",
                    description="The sign of the Laughing Dragon swings above the tavern door."
                ),
                Exit(
                    source_room_id=rooms["tavern"].id,
                    destination_room_id=rooms["village_square"].id,
                    direction="east",
                    name="tavern exit",
                    description="The door leads back to the village square."
                ),
                
                Exit(
                    source_room_id=rooms["village_square"].id,
                    destination_room_id=rooms["general_store"].id,
                    direction="north",
                    name="general store",
                    description="A small shop with various goods displayed in the window."
                ),
                Exit(
                    source_room_id=rooms["general_store"].id,
                    destination_room_id=rooms["village_square"].id,
                    direction="south",
                    name="store exit",
                    description="The door leads back to the village square."
                ),
                
                # Northern path
                Exit(
                    source_room_id=rooms["general_store"].id,
                    destination_room_id=rooms["north_path"].id,
                    direction="north",
                    name="north path",
                    description="A path leads north toward the edge of the village."
                ),
                Exit(
                    source_room_id=rooms["north_path"].id,
                    destination_room_id=rooms["general_store"].id,
                    direction="south",
                    name="south path",
                    description="The path leads back to the general store."
                ),
                
                Exit(
                    source_room_id=rooms["north_path"].id,
                    destination_room_id=rooms["village_gate"].id,
                    direction="north",
                    name="village gate",
                    description="You can see the village gate up ahead."
                ),
                Exit(
                    source_room_id=rooms["village_gate"].id,
                    destination_room_id=rooms["north_path"].id,
                    direction="south",
                    name="village path",
                    description="The path leads back into the village."
                ),
                
                Exit(
                    source_room_id=rooms["village_gate"].id,
                    destination_room_id=rooms["forest_edge"].id,
                    direction="north",
                    name="forest trail",
                    description="A trail leads into the darkness of the forest."
                ),
                Exit(
                    source_room_id=rooms["forest_edge"].id,
                    destination_room_id=rooms["village_gate"].id,
                    direction="south",
                    name="village gate",
                    description="The safe haven of the village lies south."
                )
            ]
            
            # Add all exits to the database
            for exit in exits:
                db.add(exit)
            
            logger.info(f"Created {len(exits)} exits")
            
            # Create some basic items
            items = [
                Item(
                    name="Rusty Sword",
                    description="A basic sword showing signs of wear but still serviceable.",
                    item_type="WEAPON",
                    room_id=rooms["blacksmith"].id,
                    properties={
                        "damage": "1d6",
                        "value": 5,
                        "weight": 2
                    }
                ),
                Item(
                    name="Wooden Shield",
                    description="A simple wooden shield reinforced with iron bands.",
                    item_type="ARMOR",
                    room_id=rooms["blacksmith"].id,
                    properties={
                        "defense": 1,
                        "value": 10,
                        "weight": 5
                    }
                ),
                Item(
                    name="Healing Potion",
                    description="A small red vial containing a healing elixir.",
                    item_type="POTION",
                    room_id=rooms["general_store"].id,
                    properties={
                        "healing": "2d4+2",
                        "value": 15,
                        "weight": 0.5
                    }
                ),
                Item(
                    name="Torch",
                    description="A wooden torch that can provide light in dark places.",
                    item_type="MISC",
                    room_id=rooms["general_store"].id,
                    properties={
                        "duration": 60,  # minutes
                        "value": 1,
                        "weight": 1
                    }
                ),
                Item(
                    name="Mug of Ale",
                    description="A frothy mug of ale that looks refreshing.",
                    item_type="FOOD",
                    room_id=rooms["tavern"].id,
                    properties={
                        "portions": 1,
                        "effects": ["restore_stamina"],
                        "value": 2,
                        "weight": 1
                    }
                )
            ]
            
            # Add all items to the database
            for item in items:
                db.add(item)
            
            logger.info(f"Created {len(items)} items")
            
            # Commit all changes
            db.commit()
            logger.info("Starter area created successfully!")
            
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating starter area: {str(e)}")


if __name__ == "__main__":
    # Run the async function to create the starter area
    asyncio.run(create_starter_area()) 