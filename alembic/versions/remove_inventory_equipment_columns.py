"""remove inventory and equipment columns

Revision ID: b92c7e53a612
Revises: a35b9c72e451
Create Date: 2024-04-26

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b92c7e53a612'
down_revision = 'a35b9c72e451'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the inventory and equipment columns from characters table
    with op.batch_alter_table('characters') as batch_op:
        batch_op.drop_column('inventory')
        batch_op.drop_column('equipment')


def downgrade():
    # Add back the inventory and equipment columns
    from app.models.base import JSON_TYPE
    with op.batch_alter_table('characters') as batch_op:
        batch_op.add_column(sa.Column('inventory', JSON_TYPE, nullable=True))
        batch_op.add_column(sa.Column('equipment', JSON_TYPE, nullable=True)) 