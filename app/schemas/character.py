from typing import Dict, List, Optional, Any
from pydantic import BaseModel, validator, Field
from enum import Enum

from app.models import CharacterRace, CharacterClass

class CharacterBase(BaseModel):
    """Base character schema with common attributes"""
    name: str
    description: Optional[str] = None
    race: CharacterRace
    character_class: CharacterClass
    
    # Ability scores
    strength: int
    intelligence: int
    wisdom: int
    dexterity: int
    constitution: int
    charisma: int
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class CharacterCreate(CharacterBase):
    """Schema for character creation"""
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

class Character(CharacterBase):
    """Schema for character responses with full details"""
    id: int
    level: int = 1
    experience: int = 0
    hit_points: int
    armor_class: int = 10
    gold: int = 0
    user_id: int
    
    # Saving throws
    save_death_ray_poison: int
    save_magic_wands: int
    save_paralysis_petrify: int
    save_dragon_breath: int
    save_spells: int
    
    # Equipment and inventory as JSON
    equipment: Dict[str, Any] = Field(default_factory=dict)
    inventory: Dict[str, Any] = Field(default_factory=dict)
    
    # Special abilities
    special_abilities: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class CharacterUpdate(BaseModel):
    """Schema for character updates"""
    name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    experience: Optional[int] = None
    hit_points: Optional[int] = None
    armor_class: Optional[int] = None
    gold: Optional[int] = None
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class CharacterState(BaseModel):
    """Schema for updating character state (HP, XP, etc.)"""
    hit_points: Optional[int] = None
    experience: Optional[int] = None
    gold: Optional[int] = None
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class CharacterStateUpdate(BaseModel):
    """Schema for comprehensive character state updates"""
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
        orm_mode = True  # For compatibility with older Pydantic 