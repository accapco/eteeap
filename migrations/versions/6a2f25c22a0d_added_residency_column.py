"""Added residency column

Revision ID: 6a2f25c22a0d
Revises: 0c7e3c229414
Create Date: 2024-05-31 17:47:00.899149

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a2f25c22a0d'
down_revision = '0c7e3c229414'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.TEXT(length=64),
               type_=sa.String(length=64),
               existing_nullable=False)
        batch_op.alter_column('f_name',
               existing_type=sa.TEXT(length=64),
               type_=sa.String(length=64),
               existing_nullable=True)
        batch_op.alter_column('m_name',
               existing_type=sa.TEXT(length=64),
               type_=sa.String(length=64),
               existing_nullable=True)
        batch_op.alter_column('l_name',
               existing_type=sa.TEXT(length=64),
               type_=sa.String(length=64),
               existing_nullable=True)
        batch_op.alter_column('ext_name',
               existing_type=sa.TEXT(length=5),
               type_=sa.String(length=5),
               existing_nullable=True)
        batch_op.alter_column('civil_status',
               existing_type=sa.TEXT(length=17),
               type_=sa.Enum('Single', 'Married', 'Legally Separated', 'Widowed'),
               existing_nullable=True)
        batch_op.alter_column('citizenship',
               existing_type=sa.TEXT(length=20),
               type_=sa.String(length=20),
               existing_nullable=True)
        batch_op.alter_column('gender',
               existing_type=sa.TEXT(length=1),
               type_=sa.Enum('M', 'F'),
               existing_nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.TEXT(length=64),
               type_=sa.String(length=64),
               existing_nullable=True)
        batch_op.alter_column('contact_no',
               existing_type=sa.TEXT(length=64),
               type_=sa.String(length=64),
               existing_nullable=True)
        batch_op.alter_column('local_address',
               existing_type=sa.TEXT(length=100),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('foreign_address',
               existing_type=sa.TEXT(length=100),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('password',
               existing_type=sa.TEXT(length=64),
               type_=sa.String(length=64),
               existing_nullable=False)
        batch_op.alter_column('user_type',
               existing_type=sa.TEXT(length=10),
               type_=sa.Enum('admin', 'instructor', 'student'),
               existing_nullable=False)
        batch_op.drop_constraint('pk_users PRIMARY KEY (id), CONSTRAINT uq_users_username', type_='unique')
        batch_op.create_unique_constraint(batch_op.f('uq_users_username'), ['username'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_users_username'), type_='unique')
        batch_op.create_unique_constraint('pk_users PRIMARY KEY (id), CONSTRAINT uq_users_username', ['username'])
        batch_op.alter_column('user_type',
               existing_type=sa.Enum('admin', 'instructor', 'student'),
               type_=sa.TEXT(length=10),
               existing_nullable=False)
        batch_op.alter_column('password',
               existing_type=sa.String(length=64),
               type_=sa.TEXT(length=64),
               existing_nullable=False)
        batch_op.alter_column('foreign_address',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(length=100),
               existing_nullable=True)
        batch_op.alter_column('local_address',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(length=100),
               existing_nullable=True)
        batch_op.alter_column('contact_no',
               existing_type=sa.String(length=64),
               type_=sa.TEXT(length=64),
               existing_nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.String(length=64),
               type_=sa.TEXT(length=64),
               existing_nullable=True)
        batch_op.alter_column('gender',
               existing_type=sa.Enum('M', 'F'),
               type_=sa.TEXT(length=1),
               existing_nullable=True)
        batch_op.alter_column('citizenship',
               existing_type=sa.String(length=20),
               type_=sa.TEXT(length=20),
               existing_nullable=True)
        batch_op.alter_column('civil_status',
               existing_type=sa.Enum('Single', 'Married', 'Legally Separated', 'Widowed'),
               type_=sa.TEXT(length=17),
               existing_nullable=True)
        batch_op.alter_column('ext_name',
               existing_type=sa.String(length=5),
               type_=sa.TEXT(length=5),
               existing_nullable=True)
        batch_op.alter_column('l_name',
               existing_type=sa.String(length=64),
               type_=sa.TEXT(length=64),
               existing_nullable=True)
        batch_op.alter_column('m_name',
               existing_type=sa.String(length=64),
               type_=sa.TEXT(length=64),
               existing_nullable=True)
        batch_op.alter_column('f_name',
               existing_type=sa.String(length=64),
               type_=sa.TEXT(length=64),
               existing_nullable=True)
        batch_op.alter_column('username',
               existing_type=sa.String(length=64),
               type_=sa.TEXT(length=64),
               existing_nullable=False)

    # ### end Alembic commands ###
