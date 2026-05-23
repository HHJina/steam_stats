"""remove tags and game_tags

Revision ID: 1e2bf0d83332
Revises: fc57c400146e
Create Date: 2026-05-22 21:42:32.488959

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1e2bf0d83332"
down_revision: Union[str, Sequence[str], None] = "fc57c400146e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("game_tags")
    op.drop_table("tags")


def downgrade() -> None:
    pass
