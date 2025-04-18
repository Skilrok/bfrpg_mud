"""merge_heads_for_items

Revision ID: 92d47ae8f612
Revises: 8453f32b9c7d, bc21e44d1b9a, merge_heads
Create Date: 2024-09-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92d47ae8f612'
down_revision = None
branch_labels = None
depends_on = None

# This migration merges multiple heads: 
# - 8453f32b9c7d (add_items_table)
# - bc21e44d1b9a (fix_characters_enum_types)
# - merge_heads (previous merge)

def upgrade():
    pass


def downgrade():
    pass 