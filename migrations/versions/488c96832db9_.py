"""empty message

Revision ID: 488c96832db9
Revises: ae346256b650
Create Date: 2022-08-25 22:27:20.381209

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '488c96832db9'
down_revision = 'ae346256b650'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('period')
    op.drop_table('week')
    op.add_column('user', sa.Column('name', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('lastname', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('address', sa.String(length=128), nullable=True))
    op.add_column('user', sa.Column('phone', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_user_address'), 'user', ['address'], unique=False)
    op.create_index(op.f('ix_user_lastname'), 'user', ['lastname'], unique=False)
    op.create_index(op.f('ix_user_name'), 'user', ['name'], unique=False)
    op.create_index(op.f('ix_user_phone'), 'user', ['phone'], unique=False)
    op.drop_column('user', 'about_me')
    op.drop_column('user', 'last_seen')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_seen', mysql.DATETIME(), nullable=True))
    op.add_column('user', sa.Column('about_me', mysql.VARCHAR(length=140), nullable=True))
    op.drop_index(op.f('ix_user_phone'), table_name='user')
    op.drop_index(op.f('ix_user_name'), table_name='user')
    op.drop_index(op.f('ix_user_lastname'), table_name='user')
    op.drop_index(op.f('ix_user_address'), table_name='user')
    op.drop_column('user', 'phone')
    op.drop_column('user', 'address')
    op.drop_column('user', 'lastname')
    op.drop_column('user', 'name')
    op.create_table('week',
    sa.Column('week_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('date_begin', sa.DATE(), nullable=True),
    sa.Column('date_end', sa.DATE(), nullable=True),
    sa.PrimaryKeyConstraint('week_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('period',
    sa.Column('id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('begin', sa.DATE(), nullable=True),
    sa.Column('end', sa.DATE(), nullable=True),
    sa.Column('reserved_user', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
