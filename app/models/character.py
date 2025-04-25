import datetime
import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.models.base import JSON_TYPE, Base

# REMOVED: import typing


class CharacterRace(str, enum.Enum):
    HUMAN = "human"
    DWARF = "dwarf"
    ELF = "elf"
    HALFLING = "halfling"


class CharacterClass(str, enum.Enum):
    FIGHTER = "fighter"
    CLERIC = "cleric"
    MAGIC_USER = "magic-user"
    THIEF = "thief"
    FIGHTER_MAGIC_USER = "fighter/magic-user"
    MAGIC_USER_THIEF = "magic-user/thief"


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)

    # Character attributes
    race = Column(Enum(CharacterRace), nullable=False)
    character_class = Column(Enum(CharacterClass), nullable=False)

    # Ability scores
    strength = Column(Integer, nullable=False)
    intelligence = Column(Integer, nullable=False)
    wisdom = Column(Integer, nullable=False)
    dexterity = Column(Integer, nullable=False)
    constitution = Column(Integer, nullable=False)
    charisma = Column(Integer, nullable=False)

    # Derived stats
    level = Column(Integer, default=1, nullable=False)
    experience = Column(Integer, default=0, nullable=False)
    hit_points = Column(Integer, nullable=False)
    armor_class = Column(Integer, default=10, nullable=False)
    gold = Column(Integer, default=0, nullable=False)

    # Saving throws
    save_death_ray_poison = Column(Integer, nullable=False)
    save_magic_wands = Column(Integer, nullable=False)
    save_paralysis_petrify = Column(Integer, nullable=False)
    save_dragon_breath = Column(Integer, nullable=False)
    save_spells = Column(Integer, nullable=False)

    # Other attributes
    languages = Column(String, default="Common", nullable=False)
    special_abilities = Column(JSON_TYPE, default=list)
    spells_known = Column(JSON_TYPE, default=list)
    thief_abilities = Column(JSON_TYPE, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="characters")
    location = relationship(
        "CharacterLocation", back_populates="character", uselist=False
    )
    journal_entries = relationship(
        "JournalEntry", back_populates="character", cascade="all, delete-orphan"
    )
    discovered_rooms = relationship(
        "RoomDiscovery", back_populates="character", cascade="all, delete-orphan"
    )
    spells = relationship(
        "CharacterSpell", back_populates="character", cascade="all, delete-orphan"
    )
    combat_participations = relationship(
        "CombatParticipant", back_populates="character", cascade="all, delete-orphan"
    )
    hirelings = relationship(
        "Hireling", back_populates="character", cascade="all, delete-orphan"
    )
    command_history = relationship(
        "CommandHistory", back_populates="character", cascade="all, delete-orphan"
    )

    # Relationship to character items
    items = relationship(
        "CharacterItem", back_populates="character", cascade="all, delete-orphan"
    )

    # Properties for backward compatibility
    @property
    def inventory(self):
        """Get inventory from items relationship in backward-compatible format"""
        result = {}
        for char_item in self.items:
            result[str(char_item.item_id)] = {
                "item_id": char_item.item_id,
                "quantity": char_item.quantity,
                "equipped": char_item.is_equipped,
                "slot": char_item.equip_slot,
            }
        return result

    @property
    def owner(self):
        """Backward compatibility property for user relationship"""
        return self.user

    @owner.setter
    def owner(self, value):
        """Setter for backward compatibility"""
        self.user = value

    @inventory.setter
    def inventory(self, value):
        """Set inventory by updating items relationship"""
        if value is None:
            # Clear all non-equipped items
            for item in list(self.items):
                if not item.is_equipped:
                    self.items.remove(item)
            return

        # Convert to dict if needed
        if not isinstance(value, dict):
            try:
                value = dict(value)
            except Exception:
                return

        # Get current items
        current_items = {item.item_id: item for item in self.items}

        # Process each item in new inventory
        for item_id_str, item_data in value.items():
            try:
                item_id = int(item_id_str)
                is_equipped = item_data.get("equipped", False)
                slot = item_data.get("slot")
                quantity = item_data.get("quantity", 1)

                # Update existing or create new
                if item_id in current_items:
                    current_items[item_id].quantity = quantity
                    current_items[item_id].is_equipped = is_equipped
                    current_items[item_id].equip_slot = slot
                else:
                    # Create new CharacterItem
                    from app.models.character_item import CharacterItem

                    new_item = CharacterItem(
                        character_id=self.id,
                        item_id=item_id,
                        quantity=quantity,
                        is_equipped=is_equipped,
                        equip_slot=slot,
                    )
                    self.items.append(new_item)

                # Remove from current_items to track what's left
                if item_id in current_items:
                    del current_items[item_id]

            except Exception as e:
                import logging

                logging.error(
                    f"Error processing inventory item {item_id_str}: {str(e)}"
                )

        # Remove items not in new inventory
        for item in list(current_items.values()):
            if not item.is_equipped:  # Keep equipped items
                self.items.remove(item)

    @property
    def equipment(self):
        """Get equipment mapping from items relationship"""
        result = {}
        for char_item in self.items:
            if char_item.is_equipped and char_item.equip_slot:
                result[char_item.equip_slot] = char_item.item_id
        return result

    @equipment.setter
    def equipment(self, value):
        """Set equipment by updating items relationship"""
        if value is None:
            # Unequip all items
            for item in self.items:
                if item.is_equipped:
                    item.is_equipped = False
                    item.equip_slot = None
            return

        # Convert to dict if needed
        if not isinstance(value, dict):
            try:
                value = dict(value)
            except Exception:
                return

        # Get current equipped items by slot
        current_slots = {}
        for item in self.items:
            if item.is_equipped and item.equip_slot:
                current_slots[item.equip_slot] = item

        # Process each slot in new equipment
        for slot, item_id in value.items():
            # Unequip current item if different
            if slot in current_slots and current_slots[slot].item_id != item_id:
                current_slots[slot].is_equipped = False
                current_slots[slot].equip_slot = None

            # Find item in inventory or create new
            item_found = False
            for item in self.items:
                if item.item_id == item_id:
                    item.is_equipped = True
                    item.equip_slot = slot
                    item_found = True
                    break

            if not item_found:
                # Create new item
                from app.models.character_item import CharacterItem

                new_item = CharacterItem(
                    character_id=self.id,
                    item_id=item_id,
                    quantity=1,
                    is_equipped=True,
                    equip_slot=slot,
                )
                self.items.append(new_item)

            # Remove from current_slots to track what's left
            if slot in current_slots:
                del current_slots[slot]

        # Unequip items no longer in equipment
        for item in current_slots.values():
            item.is_equipped = False
            item.equip_slot = None
