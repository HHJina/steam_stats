"""

Revision ID: fc57c400146e
Revises: bc8e3e444991
Create Date: 2026-05-22 18:18:34.357742

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fc57c400146e"
down_revision: Union[str, Sequence[str], None] = "bc8e3e444991"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("games", sa.Column("peak_in_game", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("games", "peak_in_game")
