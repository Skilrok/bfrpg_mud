"""merge_heads_for_password_reset

Revision ID: df3e7a9b85cd
Revises: bc21e44d1b9a, dcc21095a326
Create Date: 2024-09-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df3e7a9b85cd'
down_revision = None
branch_labels = None
depends_on = None

# Multiple heads: bc21e44d1b9a, dcc21095a326

def upgrade():
    pass


def downgrade():
    pass 