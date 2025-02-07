"""add sku to monitors

Revision ID: 9c59ef854f9f
Revises: edeb094ee1fe
Create Date: 2024-04-13 09:29:05.329907

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c59ef854f9f'
down_revision = 'edeb094ee1fe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('monitors', sa.Column('sku', sa.String(length=50), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('monitors', 'sku')
    # ### end Alembic commands ###
