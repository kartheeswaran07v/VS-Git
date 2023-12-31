"""empty message

Revision ID: ffdee6cac095
Revises: 92c4622a98da
Create Date: 2023-12-11 13:07:43.774851

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffdee6cac095'
down_revision = '92c4622a98da'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('customer2Master')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customer2Master',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=300), nullable=True),
    sa.Column('address', sa.VARCHAR(length=300), nullable=True),
    sa.Column('customer_id', sa.VARCHAR(length=300), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
