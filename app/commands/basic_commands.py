import json
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.commands import registry as command_registry_commands
from app.commands.base import CommandContext, CommandHandler, CommandResponse
from app.commands.registry import command_registry
from app.database import get_db_context
from app.models import Area, Character, Exit, Item, Room, User

logger = logging.getLogger(__name__)


class HelpCommand(CommandHandler):
    """Handler for the help command"""

    name = "help"
    aliases = ["?", "commands", "h"]
    help_text = "Display help information for available commands. Usage: help [command]"

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Show help for a specific command
        if ctx.args and len(ctx.args) > 0:
            cmd_name = ctx.args[0].lower()
            handler = command_registry.get_handler(cmd_name)

            if handler:
                return CommandResponse(
                    success=True,
                    message=f"Help for '{handler.name}':\n{handler.get_help()}",
                    data={"command": handler.name, "help_text": handler.get_help()},
                )
            else:
                return CommandResponse(
                    success=False,
                    message=f"No help available: Command '{cmd_name}' not found.",
                    errors=[f"Command '{cmd_name}' not found"],
                )

        # Show general help (list of commands)
        commands = command_registry.get_command_list()
        commands_by_name = sorted(commands, key=lambda c: c.name)

        # Categorize commands
        categories = {
            "Basic": ["help", "look", "examine"],
            "Movement": ["north", "south", "east", "west", "up", "down", "go"],
            "Character": [
                "inventory",
                "stats",
                "create",
                "race",
                "class",
                "roll",
                "standard",
                "confirm",
            ],
            "Equipment": ["equip", "unequip"],
            "Communication": ["say", "emote", "talk"],
            "Other": [],  # For any commands not in a specific category
        }

        categorized_commands = {category: [] for category in categories}

        # Sort commands into categories
        for cmd in commands_by_name:
            placed = False
            for category, cmd_list in categories.items():
                if cmd.name in cmd_list:
                    categorized_commands[category].append(cmd)
                    placed = True
                    break

            if not placed:
                categorized_commands["Other"].append(cmd)

        # Format command list with categories
        help_text = "Available commands:\n"

        for category, cmds in categorized_commands.items():
            if not cmds:  # Skip empty categories
                continue

            help_text += f"\n== {category} Commands ==\n"
            for cmd in cmds:
                aliases = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
                help_text += f"- {cmd.name}{aliases}: {cmd.help_text.split('.')[0]}.\n"

        help_text += (
            "\nFor more information about a specific command, type: help <command>"
        )

        return CommandResponse(
            success=True,
            message=help_text,
            data={
                "commands": [
                    {"name": cmd.name, "help": cmd.help_text, "aliases": cmd.aliases}
                    for cmd in commands_by_name
                ]
            },
        )


class InventoryCommand(CommandHandler):
    """Handler for the inventory command"""

    name = "inventory"
    aliases = ["inv", "i"]
    help_text = "Check your character's inventory. Usage: inventory"

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # If no character is active, we can't check inventory
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to check inventory.",
                errors=["No active character"],
            )

        # Get the character's inventory
        inventory = ctx.character.inventory or {}

        if not inventory:
            return CommandResponse(
                success=True,
                message="Your inventory is empty.",
                data={"inventory": []},
            )

        # Format the inventory for display
        inventory_message = "You check your inventory.\n"
        equipped_items = []
        unequipped_items = []
        inventory_items = []

        # Use context manager properly with 'with' statement
        with get_db_context() as db:
            try:
                for item_id_str, item_data in inventory.items():
                    try:
                        item_id = int(item_id_str)
                        quantity = item_data.get("quantity", 1)
                        equipped = item_data.get("equipped", False)
                        slot = item_data.get("slot", None)

                        # Look up item details
                        db_item = db.query(Item).filter(Item.id == item_id).first()

                        if db_item:
                            item_name = db_item.name
                            item_description = (
                                f" - {db_item.description}"
                                if db_item.description
                                else ""
                            )
                            quantity_text = f" (x{quantity})" if quantity > 1 else ""
                            slot_text = f" [{slot}]" if slot else ""

                            # Include item_type and other properties
                            item_info = {
                                "id": item_id,
                                "name": item_name,
                                "description": db_item.description,
                                "quantity": quantity,
                                "equipped": equipped,
                                "slot": slot or db_item.equip_slot,
                                "item_type": db_item.item_type or "miscellaneous",
                                "weight": db_item.weight or 0,
                                "value": db_item.value or 0,
                                "is_equippable": bool(db_item.is_equippable),
                                "equip_slot": db_item.equip_slot or "",
                                "damage": db_item.damage or "",
                                "armor_class": db_item.armor_class or 0,
                                "properties": db_item.properties or {},
                            }

                            item_line = f"- {item_name}{quantity_text}{slot_text}{item_description}"

                            if equipped:
                                equipped_items.append((item_line, item_info))
                            else:
                                unequipped_items.append((item_line, item_info))
                        else:
                            item_info = {
                                "id": item_id,
                                "name": f"Unknown Item ({item_id})",
                                "quantity": quantity,
                                "equipped": equipped,
                            }

                            item_line = f"- Unknown item (ID: {item_id}){' (equipped)' if equipped else ''}"

                            if equipped:
                                equipped_items.append((item_line, item_info))
                            else:
                                unequipped_items.append((item_line, item_info))
                    except Exception as e:
                        logger.error(
                            f"Error processing inventory item {item_id_str}: {str(e)}"
                        )
                        item_line = f"- Error processing item {item_id_str}"
                        unequipped_items.append((item_line, {"error": str(e)}))

                # Sort equipped items by slot for better organization
                equipped_items.sort(key=lambda x: str(x[1].get("slot", "zzz")))

                # Add equipped items first
                if equipped_items:
                    inventory_message += "\nEquipped items:\n"
                    for item_line, _ in equipped_items:
                        inventory_message += f"{item_line}\n"

                # Then unequipped items
                if unequipped_items:
                    inventory_message += "\nIn your backpack:\n"
                    for item_line, _ in unequipped_items:
                        inventory_message += f"{item_line}\n"

                # Combine items for return data
                inventory_items = [
                    item[1] for item in equipped_items + unequipped_items
                ]
            except Exception as e:
                logger.error(f"Error processing inventory: {str(e)}")
                return CommandResponse(
                    success=False,
                    message=f"An error occurred while retrieving your inventory: {str(e)}",
                    errors=[str(e)],
                )

        return CommandResponse(
            success=True,
            message=inventory_message,
            data={"inventory": inventory_items},
        )


class ExamineCommand(CommandHandler):
    """Handler for the examine command"""

    name = "examine"
    aliases = ["exam", "ex", "x"]
    help_text = (
        "Examine an object, character, or feature closely. Usage: examine <target>"
    )

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # If no character is active, we can't examine
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to examine things.",
                errors=["No active character"],
            )

        # Must have a target
        if not ctx.args:
            return CommandResponse(
                success=False,
                message="What do you want to examine?",
                errors=["No target specified"],
            )

        target = " ".join(ctx.args).lower()

        # TODO: Implement object/NPC detailed examination
        return CommandResponse(
            success=True,
            message=f"You examine the {target} closely. This is a placeholder detailed description.",
            data={"target": target},
        )


class EquipCommand(CommandHandler):
    """Handler for the equip command"""

    name = "equip"
    aliases = ["wear", "wield"]
    help_text = "Equip an item from your inventory. Usage: equip <item name>. You can equip weapons (main_hand), armor (body), shields (off_hand), rings, and amulets. Armor and shields will improve your armor class."

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # If no character is active, we can't equip
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to equip items.",
                errors=["No active character"],
            )

        # Check if an item name was provided
        if not ctx.args:
            return CommandResponse(
                success=False,
                message="What do you want to equip? Usage: equip <item name>",
                errors=["No item specified"],
            )

        # Get the item name from args
        item_name = " ".join(ctx.args).lower()

        # Use the context manager properly
        with get_db_context() as db:
            try:
                # Get a fresh character from the current session to avoid session conflicts
                character = (
                    db.query(Character).filter(Character.id == ctx.character.id).first()
                )
                if not character:
                    return CommandResponse(
                        success=False,
                        message="Character not found in database.",
                        errors=["Character not found"],
                    )

                # Get inventory from the fresh character
                inventory = character.inventory or {}

                if not inventory:
                    return CommandResponse(
                        success=False,
                        message="Your inventory is empty.",
                        errors=["Empty inventory"],
                    )

                # Find the item in inventory
                found_item_id = None
                found_item_data = None

                for item_id_str, item_data in inventory.items():
                    try:
                        item_id = int(item_id_str)
                        db_item = db.query(Item).filter(Item.id == item_id).first()

                        if db_item and db_item.name.lower() == item_name:
                            found_item_id = item_id
                            found_item_data = item_data
                            break
                    except Exception as e:
                        logger.error(
                            f"Error checking inventory item {item_id_str}: {str(e)}"
                        )

                if not found_item_id:
                    # Try partial match
                    for item_id_str, item_data in inventory.items():
                        try:
                            item_id = int(item_id_str)
                            db_item = db.query(Item).filter(Item.id == item_id).first()

                            if db_item and item_name in db_item.name.lower():
                                found_item_id = item_id
                                found_item_data = item_data
                                break
                        except Exception as e:
                            logger.error(
                                f"Error checking inventory item {item_id_str}: {str(e)}"
                            )

                if not found_item_id:
                    return CommandResponse(
                        success=False,
                        message=f"You don't have '{item_name}' in your inventory.",
                        errors=["Item not found"],
                    )

                # Check if already equipped
                equipment = character.equipment or {}
                item_id_str = str(found_item_id)
                if (
                    found_item_data.get("equipped", False)
                    or item_id_str in equipment.values()
                ):
                    # Double check equipment to verify this is correct
                    logger.debug(
                        f"Item data for {found_item_id}: {found_item_data}, Equipment: {equipment}"
                    )

                    # If the item appears to be equipped but isn't in equipment, fix the inconsistency
                    if (
                        found_item_data.get("equipped", False)
                        and item_id_str not in equipment.values()
                    ):
                        logger.warning(
                            f"Inconsistent state detected: Item {found_item_id} marked as equipped but not in equipment. Fixing..."
                        )
                        inventory[item_id_str]["equipped"] = False
                        inventory[item_id_str]["slot"] = None

                        # Continue with equipping instead of returning error
                        logger.info(
                            f"Fixed inconsistency for item {found_item_id}, proceeding with equip command"
                        )
                    else:
                        return CommandResponse(
                            success=False,
                            message=f"You're already wearing or wielding that.",
                            errors=["Already equipped"],
                        )

                # Get item details
                db_item = db.query(Item).filter(Item.id == found_item_id).first()

                # Determine appropriate slot based on item type
                slot = None
                if db_item.item_type.value == "weapon":
                    slot = "main_hand"
                elif db_item.item_type.value == "armor":
                    slot = "body"
                elif db_item.item_type.value == "shield":
                    slot = "off_hand"
                elif db_item.item_type.value == "ring":
                    slot = "ring_1"  # Default to first ring slot
                elif db_item.item_type.value == "amulet":
                    slot = "neck"
                else:
                    return CommandResponse(
                        success=False,
                        message=f"You can't equip a {db_item.item_type.value}.",
                        errors=["Cannot equip item type"],
                    )

                # Check if something is already in that slot
                old_item_name = None

                if slot in equipment:
                    old_item_id = equipment[slot]
                    old_item_id_str = str(old_item_id)

                    if old_item_id_str in inventory:
                        old_db_item = (
                            db.query(Item).filter(Item.id == old_item_id).first()
                        )
                        if old_db_item:
                            old_item_name = old_db_item.name
                            inventory[old_item_id_str]["equipped"] = False
                            inventory[old_item_id_str]["slot"] = None

                # Equip the new item
                equipment[slot] = found_item_id
                inventory[item_id_str]["equipped"] = True
                inventory[item_id_str]["slot"] = slot

                # Create new dictionaries instead of modifying the existing ones
                # This ensures SQLAlchemy detects the changes
                new_equipment = dict(equipment)
                new_inventory = dict(inventory)

                # Update the character
                character.equipment = new_equipment
                character.inventory = new_inventory

                # Update armor class if needed
                if db_item.item_type.value in ["armor", "shield"]:
                    base_ac = 10
                    dex_mod = get_ability_modifier(character.dexterity)

                    # Calculate AC from equipped items
                    for slot_name, item_id in equipment.items():
                        item_id_str = str(item_id)
                        if item_id_str in inventory:
                            slot_item_data = inventory[item_id_str]
                            slot_db_item = (
                                db.query(Item).filter(Item.id == item_id).first()
                            )
                            if slot_db_item:
                                # First try to use the ac_bonus column
                                if slot_db_item.ac_bonus is not None:
                                    ac_bonus = slot_db_item.ac_bonus
                                    logger.debug(
                                        f"Using ac_bonus column value: {ac_bonus}"
                                    )
                                # Fall back to properties if column is None
                                elif (
                                    slot_db_item.properties
                                    and "ac_bonus" in slot_db_item.properties
                                ):
                                    ac_bonus = slot_db_item.properties["ac_bonus"]
                                    logger.debug(
                                        f"Using properties ac_bonus value: {ac_bonus}"
                                    )
                                if (
                                    slot_name == "body"
                                    and slot_db_item.item_type.value == "armor"
                                ):
                                    # Armor replaces base AC
                                    base_ac = ac_bonus
                                elif (
                                    slot_name == "off_hand"
                                    and slot_db_item.item_type.value == "shield"
                                ):
                                    # Shield adds to AC
                                    base_ac += ac_bonus  # In ascending AC system, higher is better

                    # Apply dexterity modifier
                    character.armor_class = (
                        base_ac + dex_mod
                    )  # Higher is better in ascending AC system

                # Use a direct SQL update to avoid session conflicts and ensure both equipment and inventory are updated together
                query = text(
                    """
                    UPDATE characters
                    SET equipment = :equipment,
                        inventory = json_set(inventory, '$.' || :item_id || '.equipped', 1),
                        inventory = json_set(inventory, '$.' || :item_id || '.slot', :slot)
                    WHERE id = :character_id
                """
                )

                db.execute(
                    query,
                    {
                        "equipment": json.dumps(new_equipment),
                        "item_id": item_id_str,
                        "slot": slot,
                        "character_id": character.id,
                    },
                )
                db.commit()

                # Refresh character from database
                db.refresh(character)

                # Build response message
                if old_item_name:
                    message = f"You remove {old_item_name} and "
                else:
                    message = "You "

                if db_item.item_type.value == "weapon":
                    message += f"wield {db_item.name}."
                elif db_item.item_type.value == "armor":
                    message += f"wear {db_item.name}."
                elif db_item.item_type.value == "shield":
                    message += f"strap {db_item.name} to your arm."
                else:
                    message += f"equip {db_item.name}."

                return CommandResponse(
                    success=True,
                    message=message,
                    data={"equipped_item": found_item_id},
                )
            except Exception as e:
                logger.exception(f"Error in EquipCommand: {e}")
                return CommandResponse(
                    success=False,
                    message="An error occurred while equipping the item.",
                    errors=[str(e)],
                )


class UnequipCommand(CommandHandler):
    """Handler for the unequip command"""

    name = "unequip"
    aliases = ["remove", "unwield"]
    help_text = "Unequip an item you're wearing or wielding. Usage: unequip <item name>. Removing armor or shields will update your armor class accordingly."

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # If no character is active, we can't unequip
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to unequip items.",
                errors=["No active character"],
            )

        # Check if an item name was provided
        if not ctx.args:
            return CommandResponse(
                success=False,
                message="What do you want to unequip? Usage: unequip <item name>",
                errors=["No item specified"],
            )

        # Get the item name from args
        item_name = " ".join(ctx.args).lower()

        # Use the context manager properly
        with get_db_context() as db:
            try:
                # Get a fresh character from the current session to avoid session conflicts
                character = (
                    db.query(Character).filter(Character.id == ctx.character.id).first()
                )
                if not character:
                    return CommandResponse(
                        success=False,
                        message="Character not found in database.",
                        errors=["Character not found"],
                    )

                # Get inventory and equipment from the fresh character
                inventory = character.inventory or {}
                equipment = character.equipment or {}

                if not equipment:
                    return CommandResponse(
                        success=False,
                        message="You're not wearing or wielding anything.",
                        errors=["No equipped items"],
                    )

                # Find the equipped item
                found_item_id = None
                found_item_slot = None

                for slot, item_id in equipment.items():
                    try:
                        db_item = db.query(Item).filter(Item.id == item_id).first()

                        if db_item and (
                            db_item.name.lower() == item_name
                            or item_name in db_item.name.lower()
                        ):
                            found_item_id = item_id
                            found_item_slot = slot
                            break
                    except Exception as e:
                        logger.error(
                            f"Error checking equipped item {item_id}: {str(e)}"
                        )

                if not found_item_id:
                    # Check if the item is in inventory but not properly marked as equipped
                    item_in_inventory = False
                    for item_id_str, item_data in inventory.items():
                        try:
                            db_item = (
                                db.query(Item)
                                .filter(Item.id == int(item_id_str))
                                .first()
                            )

                            if db_item and (
                                db_item.name.lower() == item_name
                                or item_name in db_item.name.lower()
                            ):
                                # Found the item in inventory, but it's not properly marked as equipped
                                logger.warning(
                                    f"Item '{db_item.name}' (ID: {item_id_str}) found in inventory but not in equipment. It may be in an inconsistent state."
                                )
                                item_in_inventory = True
                                break
                        except Exception as e:
                            logger.error(
                                f"Error checking inventory item {item_id_str}: {str(e)}"
                            )

                    if item_in_inventory:
                        return CommandResponse(
                            success=False,
                            message=f"You're not currently wearing or wielding '{item_name}'.",
                            errors=["Item not equipped"],
                        )
                    else:
                        return CommandResponse(
                            success=False,
                            message=f"You're not wearing or wielding '{item_name}'.",
                            errors=["Item not equipped"],
                        )

                # Debug log item ID and slot
                logger.debug(
                    f"Unequipping item ID {found_item_id} from slot {found_item_slot}"
                )

                # Get item details
                db_item = db.query(Item).filter(Item.id == found_item_id).first()

                # Remove from equipment
                new_equipment = dict(equipment)
                del new_equipment[found_item_slot]

                # Update inventory item as unequipped
                new_inventory = dict(inventory)
                item_id_str = str(found_item_id)
                if item_id_str in new_inventory:
                    new_inventory[item_id_str]["equipped"] = False
                    new_inventory[item_id_str]["slot"] = None

                # Update the character
                character.equipment = new_equipment
                character.inventory = new_inventory

                # Update armor class if needed
                if db_item.item_type.value in ["armor", "shield"]:
                    base_ac = 10
                    dex_mod = get_ability_modifier(character.dexterity)

                    # Calculate AC from remaining equipped items
                    for slot_name, item_id in new_equipment.items():
                        item_id_str = str(item_id)
                        if item_id_str in new_inventory:
                            slot_item_data = new_inventory[item_id_str]
                            slot_db_item = (
                                db.query(Item).filter(Item.id == item_id).first()
                            )
                            if slot_db_item:
                                # First try to use the ac_bonus column
                                if slot_db_item.ac_bonus is not None:
                                    ac_bonus = slot_db_item.ac_bonus
                                    logger.debug(
                                        f"Using ac_bonus column value: {ac_bonus}"
                                    )
                                # Fall back to properties if column is None
                                elif (
                                    slot_db_item.properties
                                    and "ac_bonus" in slot_db_item.properties
                                ):
                                    ac_bonus = slot_db_item.properties["ac_bonus"]
                                    logger.debug(
                                        f"Using properties ac_bonus value: {ac_bonus}"
                                    )
                                if (
                                    slot_name == "body"
                                    and slot_db_item.item_type.value == "armor"
                                ):
                                    # Armor replaces base AC
                                    base_ac = ac_bonus
                                elif (
                                    slot_name == "off_hand"
                                    and slot_db_item.item_type.value == "shield"
                                ):
                                    # Shield adds to AC
                                    base_ac += ac_bonus  # In ascending AC system, higher is better

                    # Apply dexterity modifier
                    character.armor_class = (
                        base_ac + dex_mod
                    )  # Higher is better in ascending AC system

                # Use a direct SQL update to avoid session conflicts and ensure both equipment and inventory are updated together
                query = text(
                    """
                    UPDATE characters
                    SET equipment = :equipment,
                        inventory = json_set(inventory, '$.' || :item_id || '.equipped', 0),
                        inventory = json_set(inventory, '$.' || :item_id || '.slot', NULL)
                    WHERE id = :character_id
                """
                )

                db.execute(
                    query,
                    {
                        "equipment": json.dumps(new_equipment),
                        "item_id": item_id_str,
                        "character_id": character.id,
                    },
                )
                db.commit()

                # Refresh character from database
                db.refresh(character)

                # Build response message
                if db_item.item_type.value == "weapon":
                    message = f"You sheathe {db_item.name}."
                elif db_item.item_type.value == "armor":
                    message = f"You take off {db_item.name}."
                elif db_item.item_type.value == "shield":
                    message = f"You remove {db_item.name} from your arm."
                else:
                    message = f"You unequip {db_item.name}."

                return CommandResponse(
                    success=True,
                    message=message,
                    data={"unequipped_item": found_item_id},
                )
            except Exception as e:
                logger.exception(f"Error in UnequipCommand: {e}")
                return CommandResponse(
                    success=False,
                    message="An error occurred while unequipping the item.",
                    errors=[str(e)],
                )


class StatsCommand(CommandHandler):
    """Handler for the stats command"""

    name = "stats"
    aliases = ["stat", "status"]
    help_text = "Show your character's statistics and equipment. Usage: stats"

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # If no character is active, we can't show stats
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to view stats.",
                errors=["No active character"],
            )

        # Format the character stats for display
        char = ctx.character

        # Basic character information
        stats_message = f"Character: {char.name} (Level {char.level} {char.race} {char.character_class})\n"
        stats_message += (
            f"HP: {char.hit_points}, AC: {char.armor_class}, Gold: {char.gold}\n\n"
        )

        # Ability scores
        stats_message += "Ability Scores:\n"
        ability_scores = [
            f"STR: {char.strength}",
            f"INT: {char.intelligence}",
            f"WIS: {char.wisdom}",
            f"DEX: {char.dexterity}",
            f"CON: {char.constitution}",
            f"CHA: {char.charisma}",
        ]
        stats_message += ", ".join(ability_scores) + "\n\n"

        # Saving throws
        stats_message += "Saving Throws:\n"
        saves = [
            f"Death/Poison: {char.save_death_ray_poison}",
            f"Magic Wands: {char.save_magic_wands}",
            f"Paralysis/Petrify: {char.save_paralysis_petrify}",
            f"Dragon Breath: {char.save_dragon_breath}",
            f"Spells: {char.save_spells}",
        ]
        stats_message += ", ".join(saves) + "\n\n"

        # Special abilities and languages
        if char.special_abilities:
            stats_message += "Special Abilities:\n"
            abilities_list = char.special_abilities
            stats_message += ", ".join(abilities_list) + "\n\n"

        if hasattr(char, "languages") and char.languages:
            stats_message += f"Languages: {char.languages}\n\n"

        # Equipment
        equipment = char.equipment or {}
        if equipment:
            stats_message += "Equipment:\n"

            db = get_db_context()
            try:
                for slot, item_id in equipment.items():
                    db_item = db.query(Item).filter(Item.id == item_id).first()
                    if db_item:
                        armor_bonus = ""
                        if db_item.properties and "ac_bonus" in db_item.properties:
                            if slot == "body" and db_item.item_type.value == "armor":
                                armor_bonus = f" (AC: {db_item.properties['ac_bonus']})"
                            elif (
                                slot == "off_hand"
                                and db_item.item_type.value == "shield"
                            ):
                                armor_bonus = (
                                    f" (AC Bonus: {db_item.properties['ac_bonus']})"
                                )
                        stats_message += f"{slot}: {db_item.name}{armor_bonus}\n"
                    else:
                        stats_message += f"{slot}: Unknown item (ID: {item_id})\n"
            finally:
                db.close()
        else:
            stats_message += "No equipment currently worn or wielded.\n"

        # For thief characters, show thief abilities
        if char.thief_abilities and (
            char.character_class == "thief"
            or char.character_class == "magic-user/thief"
        ):
            stats_message += "\nThief Abilities:\n"
            for ability, value in char.thief_abilities.items():
                # Format the ability name nicely
                ability_name = ability.replace("_", " ").title()
                stats_message += f"{ability_name}: {value}%\n"

        # For magic users, show known spells
        if char.spells_known and (
            char.character_class == "magic-user"
            or char.character_class == "fighter/magic-user"
            or char.character_class == "magic-user/thief"
        ):
            stats_message += "\nSpells Known:\n"
            for spell in char.spells_known:
                stats_message += f"- {spell}\n"

        return CommandResponse(
            success=True,
            message=stats_message,
            data={
                "character": {
                    "name": char.name,
                    "level": char.level,
                    "race": char.race,
                    "class": char.character_class,
                    "hp": char.hit_points,
                    "ac": char.armor_class,
                    "gold": char.gold,
                    "equipment": equipment,
                }
            },
        )


# Import ability modifier function for armor class calculations
from app.routers.characters import get_ability_modifier

# Register all command handlers
command_registry.register(HelpCommand)
command_registry.register(InventoryCommand)
command_registry.register(ExamineCommand)
command_registry.register(EquipCommand)
command_registry.register(UnequipCommand)
command_registry.register(StatsCommand)

# LookCommand removed from this file to avoid duplicate registration
# The implementation in look_commands.py will be used instead
