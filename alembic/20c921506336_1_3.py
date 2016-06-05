"""
1.3

Revision ID: 20c921506336
Revises: 2b56ad35fcd7
Create Date: 2016-05-17 21:01:23.824000

"""

# revision identifiers, used by Alembic.
revision = '20c921506336'
down_revision = '2b56ad35fcd7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('alarmtypes', sa.Column('attributes', sa.TEXT(), nullable=True, default=""))
    op.add_column('alarmsections', sa.Column('attributes', sa.TEXT(), nullable=True, default=""))
    ### end Alembic commands ###


def downgrade():
    op.drop_column('alarmtypes', 'attributes')
    op.drop_column('alarmsections', 'attributes')
    ### end Alembic commands ###
