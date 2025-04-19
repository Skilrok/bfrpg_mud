"""add_password_reset_fields

Revision ID: c2e5d4f6a78b
Revises: df3e7a9b85cd
Create Date: 2024-09-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2e5d4f6a78b'
down_revision = 'df3e7a9b85cd'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("reset_token", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("reset_token_expiry", sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("reset_token")
        batch_op.drop_column("reset_token_expiry") 