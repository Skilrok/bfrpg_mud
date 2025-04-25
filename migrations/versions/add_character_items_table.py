"""add character_items table

Revision ID: a35b9c72e451
Revises: af9d6581c320
Create Date: 2024-04-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'a35b9c72e451'
down_revision = None  # Set to None for first migration, or specific revision ID if you know it
branch_labels = None
depends_on = None


def upgrade():
    # Create character_items table
    op.create_table(
        'character_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_equipped', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('equip_slot', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add unique constraint for character_id and equip_slot (when equipped)
    op.create_index(
        'idx_character_equip_slot', 
        'character_items', 
        ['character_id', 'equip_slot'], 
        unique=True,
        postgresql_where=sa.text('is_equipped = true AND equip_slot IS NOT NULL'),
        sqlite_where=sa.text('is_equipped = 1 AND equip_slot IS NOT NULL')
    )
    
    # Add indexes for performance
    op.create_index('idx_character_items_character_id', 'character_items', ['character_id'])
    op.create_index('idx_character_items_item_id', 'character_items', ['item_id'])
    op.create_index('idx_character_items_equipped', 'character_items', ['is_equipped'])


def downgrade():
    # Drop indexes first
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    indexes = inspector.get_indexes('character_items')
    
    for index in indexes:
        op.drop_index(index['name'], table_name='character_items')
    
    # Drop the table
    op.drop_table('character_items') 