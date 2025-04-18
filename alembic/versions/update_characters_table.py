"""update_characters_table

Revision ID: af9d6581c320
Revises: 
Create Date: 2024-09-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision = 'af9d6581c320'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to the characters table
    with op.batch_alter_table('characters') as batch_op:
        # Race and class
        batch_op.add_column(sa.Column('race', sa.String(), nullable=False, server_default='human'))
        batch_op.add_column(sa.Column('character_class', sa.String(), nullable=False, server_default='fighter'))
        
        # Ability scores
        batch_op.add_column(sa.Column('strength', sa.Integer(), nullable=False, server_default='10'))
        batch_op.add_column(sa.Column('intelligence', sa.Integer(), nullable=False, server_default='10'))
        batch_op.add_column(sa.Column('wisdom', sa.Integer(), nullable=False, server_default='10'))
        batch_op.add_column(sa.Column('dexterity', sa.Integer(), nullable=False, server_default='10'))
        batch_op.add_column(sa.Column('constitution', sa.Integer(), nullable=False, server_default='10'))
        batch_op.add_column(sa.Column('charisma', sa.Integer(), nullable=False, server_default='10'))
        
        # Combat stats
        batch_op.add_column(sa.Column('hit_points', sa.Integer(), nullable=False, server_default='1'))
        batch_op.add_column(sa.Column('armor_class', sa.Integer(), nullable=False, server_default='10'))
        
        # Equipment and inventory
        batch_op.add_column(sa.Column('equipment', sa.JSON(), nullable=True, server_default='{}'))
        batch_op.add_column(sa.Column('inventory', sa.JSON(), nullable=True, server_default='{}'))
        batch_op.add_column(sa.Column('gold', sa.Integer(), nullable=False, server_default='0'))
        
        # Languages
        batch_op.add_column(sa.Column('languages', sa.String(), nullable=True, server_default='Common'))
        
        # Saving throws
        batch_op.add_column(sa.Column('save_death_ray_poison', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('save_magic_wands', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('save_paralysis_petrify', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('save_dragon_breath', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('save_spells', sa.Integer(), nullable=True))
        
        # Special abilities
        batch_op.add_column(sa.Column('special_abilities', sa.JSON(), nullable=True, server_default='[]'))
        
        # Spells
        batch_op.add_column(sa.Column('spells_known', sa.JSON(), nullable=True, server_default='[]'))
        
        # Thief abilities
        batch_op.add_column(sa.Column('thief_abilities', sa.JSON(), nullable=True, server_default='{}'))


def downgrade():
    # Remove added columns
    with op.batch_alter_table('characters') as batch_op:
        batch_op.drop_column('race')
        batch_op.drop_column('character_class')
        batch_op.drop_column('strength')
        batch_op.drop_column('intelligence')
        batch_op.drop_column('wisdom')
        batch_op.drop_column('dexterity')
        batch_op.drop_column('constitution')
        batch_op.drop_column('charisma')
        batch_op.drop_column('hit_points')
        batch_op.drop_column('armor_class')
        batch_op.drop_column('equipment')
        batch_op.drop_column('inventory')
        batch_op.drop_column('gold')
        batch_op.drop_column('languages')
        batch_op.drop_column('save_death_ray_poison')
        batch_op.drop_column('save_magic_wands')
        batch_op.drop_column('save_paralysis_petrify')
        batch_op.drop_column('save_dragon_breath')
        batch_op.drop_column('save_spells')
        batch_op.drop_column('special_abilities')
        batch_op.drop_column('spells_known')
        batch_op.drop_column('thief_abilities') 