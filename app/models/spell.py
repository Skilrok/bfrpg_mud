"""
Models for magic spells in the BFRPG MUD.
This includes spells and character-specific spell lists.
"""

import enum

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import JSON_TYPE, Base


class SpellSchool(str, enum.Enum):
    """Types of spell schools/categories"""

    ABJURATION = "abjuration"
    CONJURATION = "conjuration"
    DIVINATION = "divination"
    ENCHANTMENT = "enchantment"
    EVOCATION = "evocation"
    ILLUSION = "illusion"
    NECROMANCY = "necromancy"
    TRANSMUTATION = "transmutation"
    CLERICAL = "clerical"  # For cleric spells


class Spell(Base):
    """Model representing a magic spell"""

    __tablename__ = "spells"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    level = Column(Integer, nullable=False)  # Spell level 1-9
    school = Column(String, nullable=True)  # Spell school
    casting_time = Column(String, nullable=True)
    range = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    components = Column(String, nullable=True)  # V, S, M components
    is_ritual = Column(Boolean, default=False)
    spell_class = Column(String, nullable=False)  # magic-user, cleric, etc.
    properties = Column(JSON_TYPE, default=dict)  # Additional spell properties

    # Relationships
    character_spells = relationship("CharacterSpell", back_populates="spell")

    @property
    def is_reversible(self):
        """Helper to check if spell can be reversed"""
        return self.properties.get("reversible", False)

    @property
    def material_components(self):
        """Get the material components for the spell"""
        return self.properties.get("material_components", [])


class CharacterSpell(Base):
    """Association model linking characters to their known spells"""

    __tablename__ = "character_spells"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(
        Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    spell_id = Column(
        Integer, ForeignKey("spells.id", ondelete="CASCADE"), nullable=False
    )
    is_prepared = Column(Boolean, default=False)  # For prepared spellcasters
    times_cast = Column(Integer, default=0)  # Track spell usage

    # Ensure a character can't have the same spell twice
    __table_args__ = (
        UniqueConstraint("character_id", "spell_id", name="uix_character_spell"),
    )

    # Relationships
    character = relationship("Character")
    spell = relationship("Spell", back_populates="character_spells")

    def prepare(self):
        """Mark the spell as prepared"""
        self.is_prepared = True
        return self.is_prepared

    def unprepare(self):
        """Mark the spell as unprepared"""
        self.is_prepared = False
        return self.is_prepared

    def cast(self):
        """Record that the spell was cast"""
        self.times_cast += 1
        # If using the Vancian magic system, unprepare after casting
        if self.is_prepared:
            self.is_prepared = False
        return self.times_cast
