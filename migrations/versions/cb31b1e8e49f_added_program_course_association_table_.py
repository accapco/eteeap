"""Added program_course_association table for curriculum

Revision ID: cb31b1e8e49f
Revises: ffced365dacf
Create Date: 2024-06-08 13:24:48.334434

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb31b1e8e49f'
down_revision = 'ffced365dacf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('courses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('units', sa.Integer(), nullable=True))
        batch_op.drop_constraint('fk_courses_program_id_programs', type_='foreignkey')
        batch_op.drop_column('program_id')

    with op.batch_alter_table('enrollments', schema=None) as batch_op:
        batch_op.drop_column('units')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('enrollments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('units', sa.INTEGER(), nullable=True))

    with op.batch_alter_table('courses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('program_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('fk_courses_program_id_programs', 'programs', ['program_id'], ['id'])
        batch_op.drop_column('units')

    # ### end Alembic commands ###