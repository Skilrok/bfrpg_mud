"""fix_characters_enum_types

Revision ID: bc21e44d1b9a
Revises: dcc21095a326
Create Date: 2024-09-22

"""
from alembic import op
import sqlalchemy as sa
from app.models import CharacterRace, CharacterClass


# revision identifiers, used by Alembic.
revision = 'bc21e44d1b9a'
down_revision = 'dcc21095a326'
branch_labels = None
depends_on = None


def upgrade():
    # Convert string columns to enum types
    with op.batch_alter_table("characters") as batch_op:
        # First drop the existing columns
        batch_op.drop_column("race")
        batch_op.drop_column("character_class")
        
        # Then add them back with the correct enum types
        batch_op.add_column(sa.Column("race", sa.Enum(CharacterRace), nullable=False, server_default="HUMAN"))
        batch_op.add_column(sa.Column("character_class", sa.Enum(CharacterClass), nullable=False, server_default="FIGHTER"))


def downgrade():
    # Convert enum columns back to strings
    with op.batch_alter_table("characters") as batch_op:
        batch_op.drop_column("race")
        batch_op.drop_column("character_class")
        
        batch_op.add_column(sa.Column("race", sa.String(), nullable=False, server_default="human"))
        batch_op.add_column(sa.Column("character_class", sa.String(), nullable=False, server_default="fighter"))