"""Extended database schema for BFRPG MUD

Revision ID: extended_db_schema
Revises: a7a0a0e31123
Create Date: 2023-10-18 12:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "extended_db_schema"
down_revision = "a7a0a0e31123"  # Point to current state we just stamped
branch_labels = None
depends_on = None


# Helper to determine if we're using SQLite
def is_sqlite():
    from sqlalchemy.engine import Inspector

    inspector = Inspector.from_engine(op.get_bind())
    return inspector.get_dialect().name == "sqlite"


# Helper to check if a table exists
def table_exists(table_name):
    from sqlalchemy.engine import Inspector

    inspector = Inspector.from_engine(op.get_bind())
    return table_name in inspector.get_table_names()


# JSON type that works for both PostgreSQL and SQLite
JSON_TYPE = sa.JSON if not is_sqlite() else sa.Text


def upgrade():
    # --- Enhance existing tables with new columns ---

    # 1. Add additional fields to NPCs to support monsters
    if table_exists("npcs"):
        # Check if columns already exist before adding them
        inspector = inspect(op.get_bind())
        columns = [c["name"] for c in inspector.get_columns("npcs")]

        if "monster_type" not in columns:
            op.add_column("npcs", sa.Column("monster_type", sa.String(), nullable=True))
        if "challenge_rating" not in columns:
            op.add_column(
                "npcs", sa.Column("challenge_rating", sa.Float(), nullable=True)
            )
        if "treasure_table" not in columns:
            op.add_column(
                "npcs", sa.Column("treasure_table", sa.String(), nullable=True)
            )

    # --- Create new tables ---

    # 2. Combat Encounters
    if not table_exists("combat_encounters"):
        op.create_table(
            "combat_encounters",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("room_id", sa.Integer(), nullable=True),
            sa.Column("name", sa.String(), nullable=True),
            sa.Column("status", sa.String(), nullable=False, server_default="active"),
            sa.Column("round", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("initiative_order", JSON_TYPE, nullable=True),
            sa.Column("properties", JSON_TYPE, nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
                onupdate=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )

    # 3. Combat Participants
    if not table_exists("combat_participants"):
        op.create_table(
            "combat_participants",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("encounter_id", sa.Integer(), nullable=False),
            sa.Column("character_id", sa.Integer(), nullable=True),
            sa.Column("npc_id", sa.Integer(), nullable=True),
            sa.Column("initiative", sa.Integer(), nullable=True),
            sa.Column("current_hp", sa.Integer(), nullable=True),
            sa.Column("conditions", JSON_TYPE, nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
                onupdate=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.ForeignKeyConstraint(
                ["encounter_id"], ["combat_encounters.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(
                ["character_id"], ["characters.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(["npc_id"], ["npcs.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.CheckConstraint(
                "(character_id IS NULL AND npc_id IS NOT NULL) OR (character_id IS NOT NULL AND npc_id IS NULL)"
            ),
        )

    # 4. Journal Entries
    if not table_exists("journal_entries"):
        op.create_table(
            "journal_entries",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("character_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("entry_type", sa.String(), nullable=False, server_default="note"),
            sa.Column("is_completed", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("related_npc_id", sa.Integer(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
                onupdate=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.ForeignKeyConstraint(
                ["character_id"], ["characters.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(
                ["related_npc_id"], ["npcs.id"], ondelete="SET NULL"
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    # 5. Spells
    if not table_exists("spells"):
        op.create_table(
            "spells",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("level", sa.Integer(), nullable=False),
            sa.Column("school", sa.String(), nullable=True),
            sa.Column("casting_time", sa.String(), nullable=True),
            sa.Column("range", sa.String(), nullable=True),
            sa.Column("duration", sa.String(), nullable=True),
            sa.Column("components", sa.String(), nullable=True),
            sa.Column("is_ritual", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("spell_class", sa.String(), nullable=False),
            sa.Column("properties", JSON_TYPE, nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
                onupdate=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_spells_name"), "spells", ["name"], unique=False)

    # 6. Character Spells (association table)
    if not table_exists("character_spells"):
        op.create_table(
            "character_spells",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("character_id", sa.Integer(), nullable=False),
            sa.Column("spell_id", sa.Integer(), nullable=False),
            sa.Column("is_prepared", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("times_cast", sa.Integer(), nullable=False, server_default="0"),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
                onupdate=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.ForeignKeyConstraint(
                ["character_id"], ["characters.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(["spell_id"], ["spells.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("character_id", "spell_id"),
        )

    # 7. Room Discoveries
    if not table_exists("room_discoveries"):
        op.create_table(
            "room_discoveries",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("character_id", sa.Integer(), nullable=False),
            sa.Column("room_id", sa.Integer(), nullable=False),
            sa.Column("is_visited", sa.Boolean(), nullable=False, server_default="1"),
            sa.Column(
                "discovery_date",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
                onupdate=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.ForeignKeyConstraint(
                ["character_id"], ["characters.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("character_id", "room_id"),
        )

    # --- Create indexes for performance optimization ---

    # Helper function to check if index exists
    def index_exists(table_name, index_name):
        inspector = inspect(op.get_bind())
        indices = [idx["name"] for idx in inspector.get_indexes(table_name)]
        return index_name in indices

    # Character indexes
    if table_exists("characters"):
        if not index_exists("characters", "ix_characters_user_id"):
            op.create_index(
                op.f("ix_characters_user_id"), "characters", ["user_id"], unique=False
            )
        if not index_exists("characters", "ix_characters_level"):
            op.create_index(
                op.f("ix_characters_level"), "characters", ["level"], unique=False
            )

    # Room indexes
    if table_exists("rooms"):
        if not index_exists("rooms", "ix_rooms_coords"):
            op.create_index(
                op.f("ix_rooms_coords"), "rooms", ["x", "y", "z"], unique=False
            )
        if not index_exists("rooms", "ix_rooms_room_type"):
            op.create_index(
                op.f("ix_rooms_room_type"), "rooms", ["room_type"], unique=False
            )

    # Exit indexes
    if table_exists("exits"):
        if not index_exists("exits", "ix_exits_source_room_id"):
            op.create_index(
                op.f("ix_exits_source_room_id"),
                "exits",
                ["source_room_id"],
                unique=False,
            )
        if not index_exists("exits", "ix_exits_destination_room_id"):
            op.create_index(
                op.f("ix_exits_destination_room_id"),
                "exits",
                ["destination_room_id"],
                unique=False,
            )

    # Room content indexes
    if table_exists("room_items"):
        if not index_exists("room_items", "ix_room_items_room_id"):
            op.create_index(
                op.f("ix_room_items_room_id"), "room_items", ["room_id"], unique=False
            )

    if table_exists("room_npcs"):
        if not index_exists("room_npcs", "ix_room_npcs_room_id"):
            op.create_index(
                op.f("ix_room_npcs_room_id"), "room_npcs", ["room_id"], unique=False
            )

    # Combat indexes
    if table_exists("combat_encounters"):
        if not index_exists("combat_encounters", "ix_combat_encounters_room_id"):
            op.create_index(
                op.f("ix_combat_encounters_room_id"),
                "combat_encounters",
                ["room_id"],
                unique=False,
            )

    if table_exists("combat_participants"):
        if not index_exists(
            "combat_participants", "ix_combat_participants_character_id"
        ):
            op.create_index(
                op.f("ix_combat_participants_character_id"),
                "combat_participants",
                ["character_id"],
                unique=False,
            )
        if not index_exists("combat_participants", "ix_combat_participants_npc_id"):
            op.create_index(
                op.f("ix_combat_participants_npc_id"),
                "combat_participants",
                ["npc_id"],
                unique=False,
            )

    # Character location indexes
    if table_exists("character_locations"):
        if not index_exists(
            "character_locations", "ix_character_locations_character_id"
        ):
            op.create_index(
                op.f("ix_character_locations_character_id"),
                "character_locations",
                ["character_id"],
                unique=False,
            )
        if not index_exists("character_locations", "ix_character_locations_room_id"):
            op.create_index(
                op.f("ix_character_locations_room_id"),
                "character_locations",
                ["room_id"],
                unique=False,
            )


def downgrade():
    # Only attempt to drop indexes if the tables exist

    # Character location indexes
    if table_exists("character_locations"):
        op.drop_index(
            op.f("ix_character_locations_room_id"), table_name="character_locations"
        )
        op.drop_index(
            op.f("ix_character_locations_character_id"),
            table_name="character_locations",
        )

    # Combat indexes
    if table_exists("combat_participants"):
        op.drop_index(
            op.f("ix_combat_participants_npc_id"), table_name="combat_participants"
        )
        op.drop_index(
            op.f("ix_combat_participants_character_id"),
            table_name="combat_participants",
        )

    if table_exists("combat_encounters"):
        op.drop_index(
            op.f("ix_combat_encounters_room_id"), table_name="combat_encounters"
        )

    # Room content indexes
    if table_exists("room_npcs"):
        op.drop_index(op.f("ix_room_npcs_room_id"), table_name="room_npcs")

    if table_exists("room_items"):
        op.drop_index(op.f("ix_room_items_room_id"), table_name="room_items")

    # Exit indexes
    if table_exists("exits"):
        op.drop_index(op.f("ix_exits_destination_room_id"), table_name="exits")
        op.drop_index(op.f("ix_exits_source_room_id"), table_name="exits")

    # Room indexes
    if table_exists("rooms"):
        op.drop_index(op.f("ix_rooms_room_type"), table_name="rooms")
        op.drop_index(op.f("ix_rooms_coords"), table_name="rooms")

    # Character indexes
    if table_exists("characters"):
        op.drop_index(op.f("ix_characters_level"), table_name="characters")
        op.drop_index(op.f("ix_characters_user_id"), table_name="characters")

    # Spell index
    if table_exists("spells"):
        op.drop_index(op.f("ix_spells_name"), table_name="spells")

    # Drop tables
    if table_exists("room_discoveries"):
        op.drop_table("room_discoveries")

    if table_exists("character_spells"):
        op.drop_table("character_spells")

    if table_exists("spells"):
        op.drop_table("spells")

    if table_exists("journal_entries"):
        op.drop_table("journal_entries")

    if table_exists("combat_participants"):
        op.drop_table("combat_participants")

    if table_exists("combat_encounters"):
        op.drop_table("combat_encounters")

    # Drop added columns
    if table_exists("npcs"):
        inspector = inspect(op.get_bind())
        columns = [c["name"] for c in inspector.get_columns("npcs")]

        if "treasure_table" in columns:
            op.drop_column("npcs", "treasure_table")

        if "challenge_rating" in columns:
            op.drop_column("npcs", "challenge_rating")

        if "monster_type" in columns:
            op.drop_column("npcs", "monster_type")
