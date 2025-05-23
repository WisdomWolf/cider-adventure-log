"""Add image field to Product model

Revision ID: aec9b9e1edda
Revises: 28ed2b97023f
Create Date: 2025-03-18 23:56:41.821381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aec9b9e1edda'
down_revision = '28ed2b97023f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.LargeBinary(), nullable=True))
        batch_op.drop_column('image_url')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.VARCHAR(length=255), nullable=True))
        batch_op.drop_column('image')

    # ### end Alembic commands ###
