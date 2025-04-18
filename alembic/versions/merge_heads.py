"""merge_heads

Revision ID: dcc21095a326
Revises: initial, af9d6581c320
Create Date: 2024-09-22

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dcc21095a326'
down_revision = None
branch_labels = None
depends_on = None

# Multi-head merge
depends_on = ('initial', 'af9d6581c320')


def upgrade():
    pass


def downgrade():
    pass 