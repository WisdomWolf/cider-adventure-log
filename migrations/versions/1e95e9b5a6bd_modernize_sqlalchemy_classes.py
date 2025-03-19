"""Modernize SQLAlchemy classes

Revision ID: 1e95e9b5a6bd
Revises: 1785cf887bf3
Create Date: 2025-03-19 17:15:11.774786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e95e9b5a6bd'
down_revision = '1785cf887bf3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_product')
    with op.batch_alter_table('barcode', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))

    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.alter_column('description',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.drop_column('barcode')

    with op.batch_alter_table('rating', schema=None) as batch_op:
        batch_op.add_column(sa.Column('purchase_location', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('consumption_location', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('consumption_method', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.alter_column('comment',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('rating', schema=None) as batch_op:
        batch_op.alter_column('comment',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.drop_column('created_at')
        batch_op.drop_column('consumption_method')
        batch_op.drop_column('consumption_location')
        batch_op.drop_column('purchase_location')

    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('barcode', sa.VARCHAR(length=100), nullable=True))
        batch_op.alter_column('description',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.drop_column('created_at')

    with op.batch_alter_table('barcode', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    op.create_table('_alembic_tmp_product',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('image', sa.BLOB(), nullable=True),
    sa.Column('flavor', sa.VARCHAR(length=100), nullable=False),
    sa.Column('brand', sa.VARCHAR(length=100), nullable=False),
    sa.Column('description', sa.VARCHAR(), nullable=True),
    sa.Column('timestamp', sa.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
