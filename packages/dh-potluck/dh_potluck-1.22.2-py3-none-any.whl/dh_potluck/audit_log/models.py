import enum

from sqlalchemy import JSON, Column, Enum, Integer, String
from sqlalchemy.dialects import mysql


class Operation(enum.Enum):
    insert = 'insert'
    update = 'update'
    delete = 'delete'


class AuditLog:
    """
    This table is populated via MySQL triggers. See ./trigger_templates for the
    implementation of these triggers.
    """

    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True)
    timestamp = Column(mysql.DATETIME(fsp=6), nullable=False)
    # Represents the method or entity that made the change. Typical values are:
    #   * `user` - A Flask user, authenticated or unauthenticated
    #   * `service` - An internal service using an `Application` token
    #   * `celery_task`
    #   * `alembic_migration`
    #   * `click_command`
    #   * `sqlalchemy` - A change made via SQLAlchemy ORM but not in the context of a request or
    #      one of the above methods
    #   * `mysql` - A change made via a raw MySQL command either via `conn.execute()` or via a SQL
    #      client
    updated_by_type = Column(String(255))

    # Values for each of the above types are:
    #   * `user` - The user id or 'unauthenticated'
    #   * `service` - Empty (until we can individually identify services making requests)
    #   * `celery_task` - The Celery task name
    #   * `alembic_migration` - The Alembic migration revision number
    #   * `click_command` - The Click command name
    #   * `sqlalchemy` - Empty
    #   * `mysql` - The MySQL user
    updated_by_id = Column(String(255))

    # The IP or hostname of the user making the request
    updated_by_ip = Column(String(255))
    table_name = Column(String(64), nullable=False)
    object_id = Column(String(64), nullable=False)
    operation = Column(Enum(Operation), nullable=False)
    old_data = Column(JSON)
    changed_data = Column(JSON)
