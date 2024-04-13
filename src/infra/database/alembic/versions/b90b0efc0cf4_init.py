"""init

Revision ID: b90b0efc0cf4
Revises:
Create Date: 2024-04-11 05:46:01.616889

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b90b0efc0cf4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'monitors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('eui', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('monitor_type', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_monitors')),
        sa.UniqueConstraint('eui', name=op.f('uq_monitors_eui')),
    )
    op.create_table(
        'monitor_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('monitor_id', sa.UUID(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(
            ['monitor_id'], ['monitors.eui'], name='fk_data_monitors_monitor_id', ondelete='RESTRICT'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_monitor_data')),
    )
    op.create_table(
        'students_register',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.UUID(), nullable=False),
        sa.Column('student', sa.String(length=50), nullable=False),
        sa.Column('heard_rate_monitor_id', sa.UUID(), nullable=False),
        sa.Column('blod_preasure_monitor_id', sa.UUID(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ['blod_preasure_monitor_id'],
            ['monitors.eui'],
            name='fk_students_register_blod_preasure_monitor_id',
            ondelete='RESTRICT',
        ),
        sa.ForeignKeyConstraint(
            ['heard_rate_monitor_id'], ['monitors.eui'], name='fk_students_register_heard_rate_monitor_id', ondelete='RESTRICT'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_students_register')),
        sa.UniqueConstraint('blod_preasure_monitor_id', 'active', name='u_blod_preasure_active'),
        sa.UniqueConstraint('heard_rate_monitor_id', 'active', name='u_heard_rate_active'),
        sa.UniqueConstraint('uuid', name=op.f('uq_students_register_uuid')),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('students_register')
    op.drop_table('monitor_data')
    op.drop_table('monitors')
    # ### end Alembic commands ###
