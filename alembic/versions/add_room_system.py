"""add_room_system

Revision ID: add_room_system
Revises: bc21e44d1b9a
Create Date: 2024-09-24

"""
from alembic import op
import sqlalchemy as sa
from app.models import RoomType
from app.models.base import JSON_TYPE

# revision identifiers, used by Alembic.
revision = 'add_room_system'
down_revision = 'bc21e44d1b9a'
branch_labels = None
depends_on = None


def upgrade():
    # Create areas table
    op.create_table(
        'areas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create rooms table
    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('room_type', sa.Enum(RoomType), nullable=False),
        sa.Column('x', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('y', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('z', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('area_id', sa.Integer(), nullable=True),
        sa.Column('exits', JSON_TYPE, nullable=True),
        sa.Column('is_dark', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('properties', JSON_TYPE, nullable=True),
        sa.ForeignKeyConstraint(['area_id'], ['areas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create room_items table
    op.create_table(
        'room_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('properties', JSON_TYPE, nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create room_npcs table
    op.create_table(
        'room_npcs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('npc_id', sa.Integer(), nullable=False),
        sa.Column('properties', JSON_TYPE, nullable=True),
        sa.ForeignKeyConstraint(['npc_id'], ['npcs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create character_locations table
    op.create_table(
        'character_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=True),
        sa.Column('x', sa.Integer(), nullable=True),
        sa.Column('y', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create a starting room
    op.execute(
        """
        INSERT INTO areas (id, name, description) 
        VALUES (1, 'Town of Beginnings', 'The starting town for new adventurers.')
        """
    )
    
    op.execute(
        f"""
        INSERT INTO rooms (id, name, description, room_type, area_id, exits) 
        VALUES (1, 'Town Square', 'The central square of the town. Paths lead in all directions.', 'town', 1, '{{"north": 2, "east": 3, "south": 4, "west": 5}}')
        """
    )
    
    op.execute(
        f"""
        INSERT INTO rooms (id, name, description, room_type, area_id, exits) 
        VALUES (2, 'North Road', 'A road leading north out of town.', 'town', 1, '{{"south": 1}}')
        """
    )
    
    op.execute(
        f"""
        INSERT INTO rooms (id, name, description, room_type, area_id, exits) 
        VALUES (3, 'East Road', 'A road leading east out of town.', 'town', 1, '{{"west": 1}}')
        """
    )
    
    op.execute(
        f"""
        INSERT INTO rooms (id, name, description, room_type, area_id, exits) 
        VALUES (4, 'South Road', 'A road leading south out of town.', 'town', 1, '{{"north": 1}}')
        """
    )
    
    op.execute(
        f"""
        INSERT INTO rooms (id, name, description, room_type, area_id, exits) 
        VALUES (5, 'West Road', 'A road leading west out of town.', 'town', 1, '{{"east": 1}}')
        """
    )


def downgrade():
    # Drop the tables in reverse order
    op.drop_table('character_locations')
    op.drop_table('room_npcs')
    op.drop_table('room_items')
    op.drop_table('rooms')
    op.drop_table('areas') 