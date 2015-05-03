"""
1.2

Revision ID: 2b56ad35fcd7
Revises: a35c7dbf502
Create Date: 2015-04-21 14:36:41.824000

"""

# revision identifiers, used by Alembic.
revision = '2b56ad35fcd7'
down_revision = 'a35c7dbf502'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('departments', sa.Column('attributes', sa.TEXT(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    op.drop_column('departments', 'attributes')
    ### end Alembic commands ###
