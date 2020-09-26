"""empty message

Revision ID: 36d9ac8eadee
Revises: 6c08b9117f37
Create Date: 2020-09-26 18:42:01.311919

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '36d9ac8eadee'
down_revision = '6c08b9117f37'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bookings', sa.Column('start_time', sa.Text(), nullable=False))
    op.drop_column('bookings', 'time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bookings', sa.Column('time', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    op.drop_column('bookings', 'start_time')
    # ### end Alembic commands ###