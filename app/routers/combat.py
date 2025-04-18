from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import random

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user

router = APIRouter()


class CombatSession:
    """Class to manage a combat session"""
    def __init__(self, 
                 character_id: int, 
                 monster_id: Optional[int] = None,
                 monster_data: Optional[Dict[str, Any]] = None):
        self.character_id = character_id
        self.monster_id = monster_id
        self.monster_data = monster_data
        self.round = 0
        self.character_initiative = 0
        self.monster_initiative = 0
        self.log = []
        self.status = "active"
        self.surprise_round = False


# In-memory store for active combat sessions
# In a production environment, this would be stored in a database
active_combats: Dict[str, CombatSession] = {}


@router.post("/initiate")
async def initiate_combat(
    character_id: int,
    monster_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Initiate combat between a character and a monster.
    Monster data should include name, AC, HP, attack bonus, damage, etc.
    """
    # Verify the character belongs to the current user
    character = db.query(models.Character).filter(
        models.Character.id == character_id,
        models.Character.user_id == current_user.id
    ).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Create a new combat session
    combat_id = f"{character_id}_{random.randint(1000, 9999)}"
    combat_session = CombatSession(
        character_id=character_id, 
        monster_data=monster_data
    )
    
    # Check for surprise
    surprise_roll_character = random.randint(1, 6)
    surprise_roll_monster = random.randint(1, 6)
    
    if surprise_roll_character <= 2:
        combat_session.log.append(f"Character is surprised!")
        combat_session.surprise_round = True
        combat_session.round = 0  # Surprise round
    elif surprise_roll_monster <= 2:
        combat_session.log.append(f"Monster ({monster_data['name']}) is surprised!")
        combat_session.surprise_round = True
        combat_session.round = 0  # Surprise round
    else:
        combat_session.log.append("No surprise. Combat begins normally.")
        combat_session.round = 1  # First regular round
    
    active_combats[combat_id] = combat_session
    
    return {
        "combat_id": combat_id,
        "message": f"Combat initiated between {character.name} and {monster_data['name']}",
        "surprise": combat_session.surprise_round,
        "round": combat_session.round,
        "log": combat_session.log
    }


@router.post("/{combat_id}/roll_initiative")
async def roll_initiative(
    combat_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Roll initiative for a combat round"""
    if combat_id not in active_combats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combat session not found"
        )
    
    combat = active_combats[combat_id]
    
    # Verify the character belongs to the current user
    character = db.query(models.Character).filter(
        models.Character.id == combat.character_id,
        models.Character.user_id == current_user.id
    ).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Calculate DEX modifier
    dex_score = character.dexterity
    dex_modifier = 0
    if dex_score == 3:
        dex_modifier = -3
    elif 4 <= dex_score <= 5:
        dex_modifier = -2
    elif 6 <= dex_score <= 8:
        dex_modifier = -1
    elif 13 <= dex_score <= 15:
        dex_modifier = 1
    elif 16 <= dex_score <= 17:
        dex_modifier = 2
    elif dex_score == 18:
        dex_modifier = 3
    
    # Roll initiative
    character_initiative = random.randint(1, 6) + dex_modifier
    monster_initiative = random.randint(1, 6)
    
    # Special case for halflings
    if character.race == models.CharacterRace.HALFLING:
        character_initiative += 1
    
    # Store initiative values
    combat.character_initiative = character_initiative
    combat.monster_initiative = monster_initiative
    
    # Determine who goes first
    if character_initiative > monster_initiative:
        first = "character"
        combat.log.append(f"{character.name} wins initiative with {character_initiative} vs. {monster_initiative}")
    elif monster_initiative > character_initiative:
        first = "monster"
        combat.log.append(f"Monster ({combat.monster_data['name']}) wins initiative with {monster_initiative} vs. {character_initiative}")
    else:
        # Tie - roll again
        first = "tie"
        combat.log.append(f"Initiative tied at {character_initiative}. Roll again.")
    
    # If this was the surprise round, increment to round 1
    if combat.round == 0:
        combat.round = 1
        combat.surprise_round = False
    
    return {
        "combat_id": combat_id,
        "character_initiative": character_initiative,
        "monster_initiative": monster_initiative,
        "first": first,
        "round": combat.round,
        "log": combat.log
    }


@router.post("/{combat_id}/attack")
async def attack(
    combat_id: str,
    attacker_type: str,  # "character" or "monster"
    attack_type: str = "melee",  # "melee" or "ranged"
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Perform an attack in combat"""
    if combat_id not in active_combats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combat session not found"
        )
    
    combat = active_combats[combat_id]
    
    # Verify the character belongs to the current user
    character = db.query(models.Character).filter(
        models.Character.id == combat.character_id,
        models.Character.user_id == current_user.id
    ).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    monster = combat.monster_data
    
    # Calculate ability modifiers
    str_score = character.strength
    dex_score = character.dexterity
    
    str_modifier = 0
    if str_score == 3:
        str_modifier = -3
    elif 4 <= str_score <= 5:
        str_modifier = -2
    elif 6 <= str_score <= 8:
        str_modifier = -1
    elif 13 <= str_score <= 15:
        str_modifier = 1
    elif 16 <= str_score <= 17:
        str_modifier = 2
    elif str_score == 18:
        str_modifier = 3
    
    dex_modifier = 0
    if dex_score == 3:
        dex_modifier = -3
    elif 4 <= dex_score <= 5:
        dex_modifier = -2
    elif 6 <= dex_score <= 8:
        dex_modifier = -1
    elif 13 <= dex_score <= 15:
        dex_modifier = 1
    elif 16 <= dex_score <= 17:
        dex_modifier = 2
    elif dex_score == 18:
        dex_modifier = 3
    
    # Get attack result
    if attacker_type == "character":
        # Calculate character attack bonus based on class and level
        attack_bonus = 1  # Default for level 1
        
        # Add ability modifier
        if attack_type == "melee":
            attack_bonus += str_modifier
        else:  # ranged
            attack_bonus += dex_modifier
        
        # Special bonus for halflings with ranged weapons
        if character.race == models.CharacterRace.HALFLING and attack_type == "ranged":
            attack_bonus += 1
        
        # Roll to hit
        attack_roll = random.randint(1, 20)
        total_attack = attack_roll + attack_bonus
        
        # Check if hit
        target_ac = monster["armor_class"]
        
        if attack_roll == 20:
            hit = True
            critical = True
        elif attack_roll == 1:
            hit = False
            critical = False
        else:
            hit = total_attack >= target_ac
            critical = False
        
        # Calculate damage if hit
        if hit:
            # Assume a default damage die of 1d6
            damage_die = 6  # Default
            damage_base = random.randint(1, damage_die)
            
            # Add STR modifier to melee damage
            if attack_type == "melee":
                damage = max(1, damage_base + str_modifier)  # Minimum 1 point of damage
            else:
                damage = damage_base
            
            # Double damage on critical hit
            if critical:
                damage *= 2
                combat.log.append(f"{character.name} scores a critical hit for {damage} damage!")
            else:
                combat.log.append(f"{character.name} hits for {damage} damage!")
            
            # Apply damage to monster
            monster["hit_points"] = max(0, monster["hit_points"] - damage)
            
            # Check if monster is defeated
            if monster["hit_points"] <= 0:
                combat.status = "character_victory"
                combat.log.append(f"{monster['name']} is defeated!")
        else:
            combat.log.append(f"{character.name} misses!")
    
    else:  # Monster attack
        # Use monster's attack bonus
        attack_bonus = monster.get("attack_bonus", 0)
        
        # Roll to hit
        attack_roll = random.randint(1, 20)
        total_attack = attack_roll + attack_bonus
        
        # Calculate character's AC, adjusting for race if necessary
        target_ac = character.armor_class
        
        # Halflings get +2 AC against larger creatures
        if character.race == models.CharacterRace.HALFLING and monster.get("size", "medium") != "small":
            target_ac += 2
        
        if attack_roll == 20:
            hit = True
            critical = True
        elif attack_roll == 1:
            hit = False
            critical = False
        else:
            hit = total_attack >= target_ac
            critical = False
        
        # Calculate damage if hit
        if hit:
            # Use monster's damage die
            damage_die = monster.get("damage_die", 6)
            damage_base = random.randint(1, damage_die)
            damage = max(1, damage_base)  # Ensure minimum 1 damage
            
            # Double damage on critical hit
            if critical:
                damage *= 2
                combat.log.append(f"{monster['name']} scores a critical hit for {damage} damage!")
            else:
                combat.log.append(f"{monster['name']} hits for {damage} damage!")
            
            # Apply damage to character
            # In a real implementation, we would update the character's hit points in the database
            # For now, we'll just track it in memory for the combat session
            character_hp = combat.get("character_hp", character.hit_points)
            character_hp = max(0, character_hp - damage)
            combat.character_hp = character_hp
            
            # Check if character is defeated
            if character_hp <= 0:
                combat.status = "monster_victory"
                combat.log.append(f"{character.name} is defeated!")
        else:
            combat.log.append(f"{monster['name']} misses!")
    
    return {
        "combat_id": combat_id,
        "round": combat.round,
        "status": combat.status,
        "character_hp": combat.get("character_hp", character.hit_points),
        "monster_hp": monster["hit_points"],
        "log": combat.log
    }


@router.get("/{combat_id}")
async def get_combat_status(
    combat_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get the current status of a combat session"""
    if combat_id not in active_combats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combat session not found"
        )
    
    combat = active_combats[combat_id]
    
    # Verify the character belongs to the current user
    character = db.query(models.Character).filter(
        models.Character.id == combat.character_id,
        models.Character.user_id == current_user.id
    ).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    return {
        "combat_id": combat_id,
        "round": combat.round,
        "status": combat.status,
        "character": {
            "id": character.id,
            "name": character.name,
            "hp": combat.get("character_hp", character.hit_points),
            "initiative": combat.character_initiative
        },
        "monster": {
            "name": combat.monster_data["name"],
            "hp": combat.monster_data["hit_points"],
            "initiative": combat.monster_initiative
        },
        "log": combat.log
    }


@router.post("/{combat_id}/end_round")
async def end_round(
    combat_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """End the current combat round and prepare for the next"""
    if combat_id not in active_combats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combat session not found"
        )
    
    combat = active_combats[combat_id]
    
    # Verify the character belongs to the current user
    character = db.query(models.Character).filter(
        models.Character.id == combat.character_id,
        models.Character.user_id == current_user.id
    ).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Check if combat has already ended
    if combat.status in ["character_victory", "monster_victory"]:
        return {
            "combat_id": combat_id,
            "message": "Combat has already ended",
            "status": combat.status,
            "log": combat.log
        }
    
    # Increment round counter
    combat.round += 1
    combat.log.append(f"Round {combat.round} begins!")
    
    # Reset initiative values
    combat.character_initiative = 0
    combat.monster_initiative = 0
    
    return {
        "combat_id": combat_id,
        "round": combat.round,
        "status": combat.status,
        "log": combat.log,
        "message": f"Round {combat.round} ready to begin"
    }


@router.delete("/{combat_id}")
async def end_combat(
    combat_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """End a combat session and clean up resources"""
    if combat_id not in active_combats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combat session not found"
        )
    
    combat = active_combats[combat_id]
    
    # Verify the character belongs to the current user
    character = db.query(models.Character).filter(
        models.Character.id == combat.character_id,
        models.Character.user_id == current_user.id
    ).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Get combat results before removing
    result = {
        "combat_id": combat_id,
        "status": combat.status,
        "rounds": combat.round,
        "log": combat.log,
        "message": "Combat has ended"
    }
    
    # Remove the combat session from active_combats
    del active_combats[combat_id]
    
    return result
