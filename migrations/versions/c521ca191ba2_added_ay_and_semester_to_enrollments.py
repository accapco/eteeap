"""Added ay and semester to enrollments

Revision ID: c521ca191ba2
Revises: 09f8efa0e2b8
Create Date: 2024-05-27 20:08:05.233407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c521ca191ba2'
down_revision = '09f8efa0e2b8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('enrollments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('academic_year', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('semester', sa.Enum('1st', '2nd'), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('enrollments', schema=None) as batch_op:
        batch_op.drop_column('semester')
        batch_op.drop_column('academic_year')

    # ### end Alembic commands ###
