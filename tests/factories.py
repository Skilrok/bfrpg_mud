"""
Test factories for creating test data.

This module contains factory functions for creating various test objects
like users, characters, and items. These functions are used by test fixtures
to create standardized test data.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.constants import CharacterClass, CharacterRace, ItemType
from app.models import Character, Hireling, Item, Room, User
from app.routers.auth import create_access_token
from app.utils import get_password_hash


def create_test_user(
    db,
    username: str = None,
    email: str = None,
    password: str = "TestPassword123!",
    is_active: bool = True,
) -> User:
    """
    Create a test user in the database

    Args:
        db: Database session
        username: Username (will be generated if None)
        email: Email (will be generated if None)
        password: Password
        is_active: Whether the user is active

    Returns:
        Created User instance
    """
    # Generate unique username if not provided
    if not username:
        unique_id = uuid.uuid4().hex[:8]
        username = f"testuser_{unique_id}"

    # Generate email if not provided
    if not email:
        email = f"{username}@example.com"

    # Create password hash
    hashed_password = f"test_hash_{password}"

    # Create user
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=is_active,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def create_test_token(user_id: int) -> str:
    """
    Create a test JWT token

    Args:
        user_id: User ID to encode in the token

    Returns:
        JWT token string
    """
    # Create token data
    token_data = {"sub": str(user_id), "exp": datetime.utcnow() + timedelta(days=1)}

    # Generate token
    token = create_access_token(token_data)

    return token


def create_test_character(
    db,
    user_id: int,
    name: str = None,
    race: CharacterRace = CharacterRace.HUMAN,
    character_class: CharacterClass = CharacterClass.FIGHTER,
    level: int = 1,
    strength: int = 16,
    intelligence: int = 10,
    wisdom: int = 10,
    dexterity: int = 12,
    constitution: int = 14,
    charisma: int = 8,
    hit_points: int = 10,
    gold: int = 100,
) -> Character:
    """
    Create a test character in the database

    Args:
        db: Database session
        user_id: Owner user ID
        name: Character name (will be generated if None)
        race: Character race
        character_class: Character class
        level: Character level
        strength: Strength attribute
        intelligence: Intelligence attribute
        wisdom: Wisdom attribute
        dexterity: Dexterity attribute
        constitution: Constitution attribute
        charisma: Charisma attribute
        hit_points: Hit points
        gold: Gold amount

    Returns:
        Created Character instance
    """
    # Generate unique name if not provided
    if not name:
        unique_id = uuid.uuid4().hex[:6]
        name = f"Test Character {unique_id}"

    # Set up equipment and inventory
    equipment = {
        "weapon": {"id": 1, "name": "Longsword"},
        "armor": {"id": 2, "name": "Leather Armor"},
    }

    inventory = [
        {"id": 3, "name": "Potion of Healing", "quantity": 2},
        {"id": 4, "name": "Torch", "quantity": 5},
    ]

    # Create character
    character = Character(
        name=name,
        description=f"A test {race.value} {character_class.value}",
        race=race.value,
        character_class=character_class.value,
        level=level,
        experience=0,
        strength=strength,
        intelligence=intelligence,
        wisdom=wisdom,
        dexterity=dexterity,
        constitution=constitution,
        charisma=charisma,
        hit_points=hit_points,
        armor_class=10,
        user_id=user_id,
        gold=gold,
        equipment=equipment,
        inventory=inventory,
    )

    db.add(character)
    db.commit()
    db.refresh(character)

    return character


def create_test_item(
    db,
    name: str = None,
    description: str = "A test item",
    item_type: ItemType = ItemType.MISCELLANEOUS,
    value: int = 10,
    weight: float = 1.0,
    properties: Optional[Dict[str, Any]] = None,
) -> Item:
    """
    Create a test item in the database

    Args:
        db: Database session
        name: Item name (will be generated if None)
        description: Item description
        item_type: Item type
        value: Item value in gold
        weight: Item weight
        properties: Item properties dictionary

    Returns:
        Created Item instance
    """
    # Generate unique name if not provided
    if not name:
        unique_id = uuid.uuid4().hex[:4]
        name = f"Test Item {unique_id}"

    # Set up properties if not provided
    if properties is None:
        properties = {"test_prop": "test_value"}

    # Create item
    item = Item(
        name=name,
        description=description,
        type=item_type.value,
        value=value,
        weight=weight,
        properties=properties,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def create_test_room(
    db,
    name: str = None,
    description: str = "A test room",
    exits: Optional[Dict[str, int]] = None,
    is_starting_room: bool = False,
) -> Room:
    """
    Create a test room in the database

    Args:
        db: Database session
        name: Room name (will be generated if None)
        description: Room description
        exits: Dictionary of exits {direction: room_id}
        is_starting_room: Whether this is a starting room

    Returns:
        Created Room instance
    """
    # Generate unique name if not provided
    if not name:
        unique_id = uuid.uuid4().hex[:4]
        name = f"Test Room {unique_id}"

    # Set up exits if not provided
    if exits is None:
        exits = {}

    # Create room
    room = Room(
        name=name,
        description=description,
        exits=exits,
        is_starting_room=is_starting_room,
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    return room


def create_test_hireling(
    db,
    name: str = None,
    level: int = 1,
    race: CharacterRace = CharacterRace.HUMAN,
    character_class: CharacterClass = CharacterClass.FIGHTER,
    salary: int = 5,
    loyalty: int = 50,
    owner_id: Optional[int] = None,
) -> Hireling:
    """
    Create a test hireling in the database

    Args:
        db: Database session
        name: Hireling name (will be generated if None)
        level: Hireling level
        race: Hireling race
        character_class: Hireling class
        salary: Salary in gold per day
        loyalty: Loyalty score (0-100)
        owner_id: Owner character ID (None = not hired)

    Returns:
        Created Hireling instance
    """
    # Generate unique name if not provided
    if not name:
        unique_id = uuid.uuid4().hex[:4]
        name = f"Test Hireling {unique_id}"

    # Create hireling
    hireling = Hireling(
        name=name,
        level=level,
        race=race.value,
        character_class=character_class.value,
        salary=salary,
        loyalty=loyalty,
        owner_id=owner_id,
        last_paid=datetime.utcnow() if owner_id else None,
    )

    db.add(hireling)
    db.commit()
    db.refresh(hireling)

    return hireling
