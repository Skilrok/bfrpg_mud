from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class CharacterItem(Base):
    """Model for items in a character's inventory"""

    __tablename__ = "character_items"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(
        Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    item_id = Column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False
    )
    quantity = Column(Integer, default=1, nullable=False)
    is_equipped = Column(Boolean, default=False, nullable=False)
    equip_slot = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    character = relationship("Character", back_populates="items")
    item = relationship("Item")

    __table_args__ = (
        # Ensure a character can't equip multiple items in same slot
        UniqueConstraint(
            "character_id",
            "equip_slot",
            name="unique_character_slot",
            deferrable=True,
            initially="DEFERRED",
        ),
    )

    def __repr__(self):
        return f"<CharacterItem(character_id={self.character_id}, item_id={self.item_id}, equipped={self.is_equipped})>"
