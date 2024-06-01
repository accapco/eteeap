"""Added honorarium column to enrollments

Revision ID: b64237f7e8ee
Revises: 0f53945af61a
Create Date: 2024-05-30 23:31:38.191063

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b64237f7e8ee'
down_revision = '0f53945af61a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('enrollments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('honorarium', sa.Enum('on process', 'released'), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('enrollments', schema=None) as batch_op:
        batch_op.drop_column('honorarium')

    # ### end Alembic commands ###