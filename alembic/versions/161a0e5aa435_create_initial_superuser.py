from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa
import os
from datetime import datetime, timezone

revision: str = '161a0e5aa435'
down_revision: Union[str, None] = '2605ffa3b292'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SUPERUSER_ID: str = str(uuid.uuid4())
SUPERUSER_EMAIL: str = "admin@example.com"
SUPERUSER_YANDEX_ID: str = "manual_superuser"


def upgrade() -> None:
    op.execute(
        f"""
        INSERT INTO users (id, yandex_id, email, is_superuser, created_at)
        VALUES (
            '{SUPERUSER_ID}',
            '{SUPERUSER_YANDEX_ID}',
            '{SUPERUSER_EMAIL}',
            true,
            '{datetime.now(timezone.utc).isoformat()}'
        )
        """
    )


def downgrade() -> None:
    op.execute(
        f"""
        DELETE FROM users WHERE yandex_id = '{SUPERUSER_YANDEX_ID}'
        """
    )
