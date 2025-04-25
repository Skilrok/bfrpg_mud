"""remove character inventory and equipment JSON columns

Revision ID: b45c9d82e452
Revises: a35b9c72e451
Create Date: 2024-04-25

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "b45c9d82e452"
down_revision = "a35b9c72e451"  # Reference to the character_items table migration
branch_labels = None
depends_on = None


def upgrade():
    # Remove the equipment and inventory JSON columns from characters table
    with op.batch_alter_table("characters") as batch_op:
        batch_op.drop_column("equipment")
        batch_op.drop_column("inventory")


def downgrade():
    # Add back the equipment and inventory JSON columns
    with op.batch_alter_table("characters") as batch_op:
        batch_op.add_column(
            sa.Column("equipment", sa.JSON(), server_default="{}", nullable=True)
        )
        batch_op.add_column(
            sa.Column("inventory", sa.JSON(), server_default="{}", nullable=True)
        )
