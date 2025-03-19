"""Removes type attribute

Revision ID: 1785cf887bf3
Revises: aec9b9e1edda
Create Date: 2025-03-19 00:47:58.695855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1785cf887bf3'
down_revision = 'aec9b9e1edda'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.alter_column('name', new_column_name='flavor')
        batch_op.drop_column('type')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('type', sa.String(length=100), nullable=False))
        batch_op.alter_column('flavor', new_column_name='name')

    # ### end Alembic commands ###
