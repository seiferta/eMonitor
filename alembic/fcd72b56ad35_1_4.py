"""
1.4

Revision ID: fcd72b56ad35
Revises: fcd72b56ad35
Create Date: 2016-07-30 21:01:23.824000

"""

# revision identifiers, used by Alembic.
revision = 'fcd72b56ad35'
down_revision = '20c921506336'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('monitorlayouts_tmp', sa.Column('id', sa.INTEGER(), nullable=False),
                    sa.Column('mid', sa.INTEGER(), nullable=False),
                    sa.Column('trigger', sa.TEXT()),
                    sa.Column('layout', sa.TEXT()),
                    sa.Column('theme', sa.VARCHAR(30)),
                    sa.Column('mintime', sa.INTEGER()),
                    sa.Column('maxtime', sa.INTEGER()),
                    sa.Column('nextid', sa.INTEGER()),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['mid'], ['monitors.id']))
    op.execute('insert into monitorlayouts_tmp select id, mid, monitorlayouts.trigger, layout, theme, mintime, maxtime, nextid from monitorlayouts;')
    op.drop_table('monitorlayouts')
    op.rename_table('monitorlayouts_tmp', 'monitorlayouts')


def downgrade():
    pass
