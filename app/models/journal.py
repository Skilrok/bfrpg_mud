"""
Model for character journal entries in the BFRPG MUD.
This includes quest logs, notes, and other character-specific records.
"""

import enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import JSON_TYPE, Base


class JournalEntryType(str, enum.Enum):
    """Types of journal entries"""

    NOTE = "note"
    QUEST = "quest"
    ACHIEVEMENT = "achievement"
    SYSTEM = "system"  # For system-generated entries


class JournalEntry(Base):
    """Model representing a journal entry for a character"""

    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(
        Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    entry_type = Column(String, nullable=False, default=JournalEntryType.NOTE)
    is_completed = Column(Boolean, default=False)  # For quest entries
    related_npc_id = Column(
        Integer, ForeignKey("npcs.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    character = relationship("Character")
    related_npc = relationship("NPC")

    @property
    def is_quest(self):
        """Helper to check if this is a quest entry"""
        return self.entry_type == JournalEntryType.QUEST

    @property
    def is_achievement(self):
        """Helper to check if this is an achievement entry"""
        return self.entry_type == JournalEntryType.ACHIEVEMENT

    def complete(self):
        """Mark a quest as completed"""
        if self.is_quest:
            self.is_completed = True
        return self.is_completed

    def add_note(self, additional_content):
        """Add additional content to an existing journal entry"""
        if additional_content:
            self.content = f"{self.content}\n\n{additional_content}"
        return self.content
