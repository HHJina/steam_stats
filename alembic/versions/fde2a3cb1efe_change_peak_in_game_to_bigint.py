"""change peak_in_game to bigint

Revision ID: fde2a3cb1efe
Revises: 1e2bf0d83332
Create Date: 2026-05-23 17:27:17.255555

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fde2a3cb1efe"
down_revision: Union[str, Sequence[str], None] = "1e2bf0d83332"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("games", "peak_in_game", type_=sa.BigInteger(), existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.alter_column("games", "peak_in_game", type_=sa.Integer(), existing_type=sa.BigInteger(), nullable=True)
