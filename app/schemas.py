from pydantic import BaseModel, EmailStr, validator, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True  # For compatibility with Pydantic v2


class TokenData(BaseModel):
    username: Optional[str] = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class CharacterRace(str, Enum):
    HUMAN = "human"
    DWARF = "dwarf"
    ELF = "elf"
    HALFLING = "halfling"


class CharacterClass(str, Enum):
    FIGHTER = "fighter"
    CLERIC = "cleric"
    MAGIC_USER = "magic-user"
    THIEF = "thief"
    FIGHTER_MAGIC_USER = "fighter/magic-user"
    MAGIC_USER_THIEF = "magic-user/thief"


class AbilityScores(BaseModel):
    strength: int = Field(..., ge=3, le=18)
    intelligence: int = Field(..., ge=3, le=18)
    wisdom: int = Field(..., ge=3, le=18)
    dexterity: int = Field(..., ge=3, le=18)
    constitution: int = Field(..., ge=3, le=18)
    charisma: int = Field(..., ge=3, le=18)

    class Config:
        from_attributes = True


class CharacterBase(BaseModel):
    name: str
    description: Optional[str] = None
    race: CharacterRace
    character_class: CharacterClass
    strength: int
    intelligence: int
    wisdom: int
    dexterity: int
    constitution: int
    charisma: int

    class Config:
        from_attributes = True


class CharacterCreate(CharacterBase):
    # We'll calculate these fields based on class/race in the endpoint
    # Don't require them from the client
    gold: Optional[int] = None
    hit_points: Optional[int] = None
    
    @validator('strength', 'intelligence', 'wisdom', 'dexterity', 'constitution', 'charisma')
    def validate_ability_range(cls, v, values, **kwargs):
        if v < 3 or v > 18:
            raise ValueError('ability scores must be between 3 and 18')
        return v
    
    @validator('character_class')
    def validate_class_ability_requirements(cls, v, values, **kwargs):
        # Check prime requisite requirements
        if 'strength' in values and v == CharacterClass.FIGHTER and values['strength'] < 9:
            raise ValueError('fighters must have at least 9 strength')
        if 'intelligence' in values and v == CharacterClass.MAGIC_USER and values['intelligence'] < 9:
            raise ValueError('magic-users must have at least 9 intelligence')
        if 'wisdom' in values and v == CharacterClass.CLERIC and values['wisdom'] < 9:
            raise ValueError('clerics must have at least 9 wisdom')
        if 'dexterity' in values and v == CharacterClass.THIEF and values['dexterity'] < 9:
            raise ValueError('thieves must have at least 9 dexterity')
            
        # Check combination class requirements (for elves)
        if v == CharacterClass.FIGHTER_MAGIC_USER:
            if 'race' in values and values['race'] != CharacterRace.ELF:
                raise ValueError('only elves can be fighter/magic-users')
            if 'strength' in values and values['strength'] < 9:
                raise ValueError('fighter/magic-users must have at least 9 strength')
            if 'intelligence' in values and values['intelligence'] < 9:
                raise ValueError('fighter/magic-users must have at least 9 intelligence')
                
        if v == CharacterClass.MAGIC_USER_THIEF:
            if 'race' in values and values['race'] != CharacterRace.ELF:
                raise ValueError('only elves can be magic-user/thieves')
            if 'intelligence' in values and values['intelligence'] < 9:
                raise ValueError('magic-user/thieves must have at least 9 intelligence')
            if 'dexterity' in values and values['dexterity'] < 9:
                raise ValueError('magic-user/thieves must have at least 9 dexterity')
                
        return v
    
    @validator('race')
    def validate_race_ability_requirements(cls, v, values, **kwargs):
        # Check race ability requirements
        if v == CharacterRace.DWARF:
            if 'constitution' in values and values['constitution'] < 9:
                raise ValueError('dwarves must have at least 9 constitution')
            if 'charisma' in values and values['charisma'] > 17:
                raise ValueError('dwarves cannot have more than 17 charisma')
                
        elif v == CharacterRace.ELF:
            if 'intelligence' in values and values['intelligence'] < 9:
                raise ValueError('elves must have at least 9 intelligence')
            if 'constitution' in values and values['constitution'] > 17:
                raise ValueError('elves cannot have more than 17 constitution')
                
        elif v == CharacterRace.HALFLING:
            if 'dexterity' in values and values['dexterity'] < 9:
                raise ValueError('halflings must have at least 9 dexterity')
            if 'strength' in values and values['strength'] > 17:
                raise ValueError('halflings cannot have more than 17 strength')
                
        return v
    
    @validator('race', 'character_class')
    def validate_class_race_combo(cls, v, values, **kwargs):
        if 'race' in values and 'character_class' in values:
            race = values['race']
            char_class = values['character_class']
            
            # Validate race/class restrictions
            if race == CharacterRace.DWARF and char_class not in [
                CharacterClass.CLERIC, CharacterClass.FIGHTER, CharacterClass.THIEF
            ]:
                raise ValueError('dwarves can only be clerics, fighters, or thieves')
                
            if race == CharacterRace.HALFLING and char_class not in [
                CharacterClass.CLERIC, CharacterClass.FIGHTER, CharacterClass.THIEF
            ]:
                raise ValueError('halflings can only be clerics, fighters, or thieves')
                
        return v

    class Config:
        from_attributes = True


class Character(CharacterBase):
    id: int
    level: int
    experience: int
    user_id: int
    hit_points: int
    armor_class: int
    gold: int = 0
    equipment: Dict[str, Any] = {}
    inventory: Dict[str, Any] = {}
    languages: str = "Common"
    save_death_ray_poison: Optional[int] = None
    save_magic_wands: Optional[int] = None
    save_paralysis_petrify: Optional[int] = None
    save_dragon_breath: Optional[int] = None
    save_spells: Optional[int] = None
    special_abilities: List[str] = []
    spells_known: List[str] = []
    thief_abilities: Dict[str, int] = {}

    class Config:
        from_attributes = True
        # Allow population by field name for SQLAlchemy relationships
        populate_by_name = True
        # Exclude private attributes from SQLAlchemy models
        exclude = {'_sa_instance_state'}


class HirelingBase(BaseModel):
    name: str
    character_class: str
    level: int = 1
    experience: int = 0
    loyalty: float = 50.0
    wage: int = 10

    class Config:
        from_attributes = True


class HirelingCreate(HirelingBase):
    pass

    class Config:
        from_attributes = True


class Hireling(HirelingBase):
    id: int
    is_available: bool
    user_id: int
    master_id: Optional[int] = None
    days_unpaid: int = 0
    last_payment_date: Optional[datetime] = None

    class Config:
        from_attributes = True  # For compatibility with Pydantic v2


# New Item Type Enum for the inventory system
class ItemType(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    POTION = "potion"
    SCROLL = "scroll"
    WAND = "wand"
    RING = "ring"
    AMMUNITION = "ammunition"
    TOOL = "tool"
    CONTAINER = "container"
    CLOTHING = "clothing"
    FOOD = "food"
    MISCELLANEOUS = "miscellaneous"


# Item base schema
class ItemBase(BaseModel):
    name: str
    description: str
    item_type: ItemType
    value: int  # Value in gold pieces
    weight: float  # Weight in pounds
    properties: Dict[str, Any] = {}  # Flexible field for item-specific properties

    class Config:
        from_attributes = True


# Schema for creating new items
class ItemCreate(ItemBase):
    pass

    class Config:
        from_attributes = True


# Item schema with database ID
class Item(ItemBase):
    id: int
    
    class Config:
        from_attributes = True


# Schema for inventory items (items in a character's inventory)
class InventoryItem(BaseModel):
    item_id: int
    quantity: int = 1
    equipped: bool = False
    slot: Optional[str] = None  # Equipment slot if equipped

    class Config:
        from_attributes = True


# Schema for adding items to inventory
class AddInventoryItem(BaseModel):
    item_id: int
    quantity: int = 1

    class Config:
        from_attributes = True


# Schema for equipping items
class EquipItem(BaseModel):
    item_id: int
    slot: str

    class Config:
        from_attributes = True


# Password reset request schema
class PasswordResetRequest(BaseModel):
    email: EmailStr
    
    class Config:
        from_attributes = True


# Password reset schema
class PasswordReset(BaseModel):
    token: str
    new_password: str
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')
        return v
    
    class Config:
        from_attributes = True


# Schema for updating character state
class CharacterStateUpdate(BaseModel):
    hit_points: Optional[int] = None
    experience: Optional[int] = None
    gold: Optional[int] = None
    level: Optional[int] = None
    armor_class: Optional[int] = None
    inventory: Optional[Dict[str, Any]] = None
    equipment: Optional[Dict[str, Any]] = None
    spells_known: Optional[List[str]] = None
    
    class Config:
        from_attributes = True
