"""add unaccent extension and indexes for projects

Revision ID: b3c8f1a2add3
Revises: 9b91acacbdf3
Create Date: 2025-10-30 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b3c8f1a2add3'
down_revision = '9b91acacbdf3'
branch_labels = None
dependencies = None


def upgrade():
    bind = op.get_bind()
    dialect = getattr(bind.dialect, 'name', None)

    if dialect == 'postgresql':
        # Create unaccent extension if available
        try:
            op.execute('CREATE EXTENSION IF NOT EXISTS unaccent;')
        except Exception:
            # best-effort: if extension cannot be created, leave a log entry
            print('Could not create unaccent extension (check permissions)')

    # Create indexes to optimize search/filter queries
    # Composite index for status + published_at
    try:
        op.create_index('ix_projects_status_published_at', 'projects', ['status', 'published_at'])
    except Exception:
        pass

    # Index for industry
    try:
        op.create_index('ix_projects_industry', 'projects', ['industry'])
    except Exception:
        pass

    # Index for stage
    try:
        op.create_index('ix_projects_stage', 'projects', ['stage'])
    except Exception:
        pass


def downgrade():
    # Drop indexes
    try:
        op.drop_index('ix_projects_stage', table_name='projects')
    except Exception:
        pass
    try:
        op.drop_index('ix_projects_industry', table_name='projects')
    except Exception:
        pass
    try:
        op.drop_index('ix_projects_status_published_at', table_name='projects')
    except Exception:
        pass

    bind = op.get_bind()
    dialect = getattr(bind.dialect, 'name', None)
    if dialect == 'postgresql':
        try:
            op.execute('DROP EXTENSION IF EXISTS unaccent;')
        except Exception:
            pass

