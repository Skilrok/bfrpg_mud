"""add_items_table

Revision ID: 8453f32b9c7d
Revises: bc21e44d1b9a
Create Date: 2024-09-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite
from app.models import ItemType


# revision identifiers, used by Alembic.
revision = '8453f32b9c7d'
down_revision = 'bc21e44d1b9a'
branch_labels = None
depends_on = None


def upgrade():
    # Create items table
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('item_type', sa.Enum(ItemType), nullable=False),
        sa.Column('value', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('weight', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('properties', sa.JSON(), nullable=True, server_default='{}'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_id'), 'items', ['id'], unique=False)
    op.create_index(op.f('ix_items_name'), 'items', ['name'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_items_name'), table_name='items')
    op.drop_index(op.f('ix_items_id'), table_name='items')
    op.drop_table('items') 