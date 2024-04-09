"""add transformer column

Revision ID: 3149aa2d0114
Revises: c939800af428
Create Date: 2023-02-03 21:44:39.429564

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '3149aa2d0114'
down_revision = 'c939800af428'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('tracks', sa.Column('transformers', sa.JSON(), nullable=True))
    op.execute('UPDATE tracks SET transformers="[]";')

def downgrade():
    op.drop_column('tracks', 'transformers')
