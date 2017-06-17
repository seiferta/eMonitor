"""
1_5

Revision ID: dc6e4d7a8716
Revises: fcd72b56ad35
Create Date: 2017-03-19 10:50:30.011000

"""

# revision identifiers, used by Alembic.
revision = 'dc6e4d7a8716'
down_revision = 'fcd72b56ad35'

branch_labels = ('default',)

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.add_column('alarmkeys', sa.Column('keyset', sa.Integer(), default=0))
    op.create_foreign_key(None, 'alarmkeys', 'alarmkeysets', ['keyset'], ['id'])
    op.add_column('alarmkeys', sa.Column('keysetitem', sa.Integer(), default=0))
    op.alter_column('monitorlayouts', 'mid', existing_type=mysql.INTEGER(display_width=11), nullable=True)


def downgrade():
    op.alter_column('monitorlayouts', 'mid', existing_type=mysql.INTEGER(display_width=11), nullable=False)
    op.drop_constraint(None, 'alarmkeys', type_='foreignkey')
    op.drop_column('alarmkeys', 'keyset')
