"""
Models for the combat system in the BFRPG MUD.
This includes combat encounters and participants in those encounters.
"""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import JSON_TYPE, Base


class CombatEncounter(Base):
    """Model representing a combat encounter in progress"""

    __tablename__ = "combat_encounters"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(
        Integer, ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True
    )
    name = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")  # active, completed, fled
    round = Column(Integer, nullable=False, default=1)
    initiative_order = Column(JSON_TYPE, default=list)  # Ordered list of combatants
    properties = Column(JSON_TYPE, default=dict)  # Additional combat properties

    # Relationships
    room = relationship("Room")
    participants = relationship(
        "CombatParticipant", back_populates="encounter", cascade="all, delete-orphan"
    )

    @property
    def is_active(self):
        """Helper to check if encounter is still active"""
        return self.status == "active"

    def next_round(self):
        """Advance to the next combat round"""
        self.round += 1
        return self.round


class CombatParticipant(Base):
    """Model representing a character or NPC in a combat encounter"""

    __tablename__ = "combat_participants"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(
        Integer, ForeignKey("combat_encounters.id", ondelete="CASCADE"), nullable=False
    )
    character_id = Column(
        Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=True
    )
    npc_id = Column(Integer, ForeignKey("npcs.id", ondelete="CASCADE"), nullable=True)

    # Combat stats for this encounter
    initiative = Column(Integer, nullable=True)
    current_hp = Column(Integer, nullable=True)
    conditions = Column(
        JSON_TYPE, default=list
    )  # statuses like poisoned, stunned, etc.

    # Ensure we have either a character OR an NPC, not both or neither
    __table_args__ = (
        CheckConstraint(
            "(character_id IS NULL AND npc_id IS NOT NULL) OR "
            "(character_id IS NOT NULL AND npc_id IS NULL)",
            name="character_or_npc_check",
        ),
    )

    # Relationships
    encounter = relationship("CombatEncounter", back_populates="participants")
    character = relationship("Character")
    npc = relationship("NPC")

    @property
    def name(self):
        """Get the name of the participant"""
        if self.character:
            return self.character.name
        elif self.npc:
            return self.npc.name
        return "Unknown"

    @property
    def max_hp(self):
        """Get the maximum hit points of the participant"""
        if self.character:
            return self.character.hit_points
        elif self.npc:
            return self.npc.hit_points
        return 0

    def take_damage(self, amount):
        """Apply damage to the participant"""
        if self.current_hp is None:
            # Initialize HP the first time damage is dealt
            if self.character:
                self.current_hp = self.character.hit_points
            elif self.npc:
                self.current_hp = self.npc.hit_points
            else:
                self.current_hp = 0

        self.current_hp = max(0, self.current_hp - amount)
        return self.current_hp

    def heal(self, amount):
        """Heal the participant"""
        if self.current_hp is None:
            # Initialize HP the first time healing is applied
            if self.character:
                self.current_hp = self.character.hit_points
            elif self.npc:
                self.current_hp = self.npc.hit_points
            else:
                self.current_hp = 0

        max_hp = self.max_hp
        self.current_hp = min(max_hp, self.current_hp + amount)
        return self.current_hp

    def add_condition(self, condition):
        """Add a condition to the participant"""
        if condition not in self.conditions:
            self.conditions.append(condition)
        return self.conditions

    def remove_condition(self, condition):
        """Remove a condition from the participant"""
        if condition in self.conditions:
            self.conditions.remove(condition)
        return self.conditions
