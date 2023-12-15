"""init

Revision ID: 4f51e05eddfe
Revises: 
Create Date: 2023-08-05 22:22:01.705277

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f51e05eddfe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=300), nullable=False),
    sa.Column('password', sa.String(length=200), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('win_count', sa.Integer(), nullable=False),
    sa.Column('lose_count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('refresh_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=200), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('refresh_token')
    op.drop_table('account')
    # ### end Alembic commands ###