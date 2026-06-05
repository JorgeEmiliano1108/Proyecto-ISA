"""Update evaluation states

Revision ID: update_states_1
Revises: 
Create Date: 2026-06-03

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_states_1'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Manual migration to update the Enum type in PostgreSQL
    # It requires dropping the default, altering type, and restoring default
    op.execute("ALTER TYPE evaluationstatus ADD VALUE IF NOT EXISTS 'RECIBIDO'")
    op.execute("ALTER TYPE evaluationstatus ADD VALUE IF NOT EXISTS 'EN_REVISION'")
    op.execute("ALTER TYPE evaluationstatus ADD VALUE IF NOT EXISTS 'APROBADO'")
    op.execute("ALTER TYPE evaluationstatus ADD VALUE IF NOT EXISTS 'NO_APROBADO'")

    # Set new default
    op.execute("ALTER TABLE evaluation_workflows ALTER COLUMN status SET DEFAULT 'RECIBIDO'::evaluationstatus")

def downgrade() -> None:
    # Downgrade is not natively supported for dropping enum values in postgres
    # We would just revert the default
    op.execute("ALTER TABLE evaluation_workflows ALTER COLUMN status SET DEFAULT 'DRAFT'::evaluationstatus")
