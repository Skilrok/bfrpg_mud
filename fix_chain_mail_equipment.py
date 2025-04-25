#!/usr/bin/env python

import json
import logging
from app.models.character import Character
from app.models.item import Item
from app.models.character_item import CharacterItem
from app.database import get_db_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_chain_mail_equipment():
    with get_db_context() as session:
        # Get character with ID 20
        char = session.query(Character).filter(Character.id == 20).first()
        if not char:
            logger.error("Character with ID 20 not found")
            return
        
        logger.info(f"Character: {char.name} (ID: {char.id})")
        logger.info(f"Current AC: {char.armor_class}")
        logger.info(f"Current Equipment JSON: {char.equipment}")
        
        # Get the Chain Mail item
        chain_mail_item = session.query(CharacterItem).filter(
            CharacterItem.character_id == char.id,
            CharacterItem.item_id == 78
        ).first()
        
        if not chain_mail_item:
            logger.error("Chain Mail not found in character's inventory")
            return
        
        # Check if Chain Mail is marked as equipped but missing from equipment JSON
        if chain_mail_item.is_equipped and 'body' not in char.equipment:
            # Add Chain Mail to the equipment JSON in the body slot
            equipment = char.equipment if char.equipment else {}
            equipment['body'] = 78
            
            # Update the equip_slot for Chain Mail
            chain_mail_item.equip_slot = 'body'
            
            # Update the character's equipment JSON
            char.equipment = equipment
            
            logger.info(f"Updated equipment JSON: {char.equipment}")
            logger.info(f"Updated Chain Mail equip_slot: {chain_mail_item.equip_slot}")
            
            # Recalculate the character's armor class
            # Get the character's dexterity modifier
            dex_mod = (char.dexterity - 10) // 2
            
            # Get the base AC from Chain Mail
            chain_mail = session.query(Item).filter(Item.id == 78).first()
            base_ac = chain_mail.armor_class or 10
            
            # Get shield bonus if any
            shield_bonus = 0
            if 'off_hand' in char.equipment:
                shield_id = char.equipment['off_hand']
                shield = session.query(Item).filter(Item.id == shield_id).first()
                if shield and shield.ac_bonus:
                    shield_bonus = shield.ac_bonus
            
            # Calculate new AC
            new_ac = base_ac + shield_bonus + dex_mod
            logger.info(f"Calculated new AC: {new_ac}")
            
            # Update character's AC
            char.armor_class = new_ac
            logger.info(f"Updated character's AC: {char.armor_class}")
            
            # Commit changes
            session.commit()
            logger.info("Changes committed to database")
        else:
            logger.info("Chain Mail is either not equipped or already in equipment JSON")

if __name__ == "__main__":
    fix_chain_mail_equipment() 