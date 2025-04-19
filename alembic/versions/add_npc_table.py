"""add_npc_table

Revision ID: add_npc_table
Revises: add_command_history
Create Date: 2024-09-25

"""
from alembic import op
import sqlalchemy as sa
from app.models.base import JSON_TYPE

# revision identifiers, used by Alembic.
revision = 'add_npc_table'
down_revision = 'add_command_history'
branch_labels = None
depends_on = None


def upgrade():
    # Create npcs table
    op.create_table(
        'npcs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('hp', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('max_hp', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('armor_class', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('hostile', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('properties', JSON_TYPE, nullable=True),
        sa.Column('dialogs', JSON_TYPE, nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes
    op.create_index(op.f('ix_npcs_name'), 'npcs', ['name'], unique=False)
    
    # Insert a sample NPC
    op.execute(
        """
        INSERT INTO npcs (id, name, description, level, hp, max_hp, hostile, dialogs)
        VALUES (1, 'Town Guard', 'A stoic guard patrolling the town square.', 2, 12, 12, 0, 
        '{"greeting": "Welcome to the Town of Beginnings.", "help": "If you need help, try the help command."}')
        """
    )
    
    # Place the NPC in the town square
    op.execute(
        """
        INSERT INTO room_npcs (room_id, npc_id)
        VALUES (1, 1)
        """
    )


def downgrade():
    # Drop tables
    op.drop_index(op.f('ix_npcs_name'), table_name='npcs')
    op.drop_table('npcs') 