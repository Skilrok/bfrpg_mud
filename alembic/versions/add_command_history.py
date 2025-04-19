"""add_command_history

Revision ID: add_command_history
Revises: add_room_system
Create Date: 2024-09-25

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_command_history'
down_revision = 'add_room_system'
branch_labels = None
depends_on = None


def upgrade():
    # Create command_history table
    op.create_table(
        'command_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=True),
        sa.Column('command', sa.String(255), nullable=False),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes
    op.create_index(op.f('ix_command_history_user_id'), 'command_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_command_history_character_id'), 'command_history', ['character_id'], unique=False)
    op.create_index(op.f('ix_command_history_command'), 'command_history', ['command'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_command_history_command'), table_name='command_history')
    op.drop_index(op.f('ix_command_history_character_id'), table_name='command_history')
    op.drop_index(op.f('ix_command_history_user_id'), table_name='command_history')
    
    # Drop table
    op.drop_table('command_history') 