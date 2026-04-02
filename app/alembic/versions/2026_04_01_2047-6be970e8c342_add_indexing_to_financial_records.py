"""Add indexing to financial records

Revision ID: 6be970e8c342
Revises: 869b63555b3f
Create Date: 2026-04-01 20:47:35.209988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6be970e8c342'
down_revision: Union[str, None] = '869b63555b3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(op.f('ix_financial_records_category'), 'financial_records', ['category'], unique=False)
    op.create_index(op.f('ix_financial_records_created_by'), 'financial_records', ['created_by'], unique=False)
    op.create_index(op.f('ix_financial_records_date'), 'financial_records', ['date'], unique=False)
    op.create_index(op.f('ix_financial_records_type'), 'financial_records', ['type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_financial_records_type'), table_name='financial_records')
    op.drop_index(op.f('ix_financial_records_date'), table_name='financial_records')
    op.drop_index(op.f('ix_financial_records_created_by'), table_name='financial_records')
    op.drop_index(op.f('ix_financial_records_category'), table_name='financial_records')
