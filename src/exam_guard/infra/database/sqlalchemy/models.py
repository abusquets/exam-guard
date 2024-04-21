import uuid

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from infra.database.sqlalchemy.sqlalchemy import metadata


monitor_types = Table(
    'monitor_types',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uuid', UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4),
    Column('sku', String(255), nullable=False, unique=True),
    Column('name', String(50), nullable=False),
    Column('monitor_type', String(50), nullable=False),
    Column('frequency', Integer, nullable=False, default=1),
)

monitors = Table(
    'monitors',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('eui', UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4),
    Column('monitor_type_id', UUID(as_uuid=True), nullable=False),
    ForeignKeyConstraint(
        ['monitor_type_id'],
        ['monitor_types.uuid'],
        name='fk_monitor_type_id_monitor_types',
        ondelete='RESTRICT',
    ),
)

monitor_data = Table(
    'monitor_data',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('monitor_id', UUID(as_uuid=True), nullable=False),
    Column('data', JSON),
    Column('ts', BigInteger, nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    ForeignKeyConstraint(
        ['monitor_id'],
        ['monitors.eui'],
        name='fk_data_monitors_monitor_id',
        ondelete='RESTRICT',
    ),
    UniqueConstraint('monitor_id', 'ts', name='u_monitor_data_monitor_id_ts'),
)
Index('monitor_data_ts_monitor_id_idx', monitor_data.c.monitor_id, monitor_data.c.ts.asc())


students_register = Table(
    'students_register',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uuid', UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4),
    Column('student', String(50), nullable=False),
    Column('active', Boolean, nullable=False, default=True),
)

students_register_monitors = Table(
    'students_register_monitors',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('student_register_id', UUID(as_uuid=True), ForeignKey('students_register.uuid', ondelete='CASCADE')),
    Column('monitor_id', UUID(as_uuid=True), ForeignKey('monitors.eui', ondelete='RESTRICT')),
    Column('value_xpath', String(255), nullable=False),
    Column('threshold', Float, nullable=False),
    Column('interval', Integer, nullable=False),
    Column('move_end_to', Integer, nullable=False, default=0),
)
