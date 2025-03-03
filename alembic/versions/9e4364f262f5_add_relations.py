"""Add relations

Revision ID: 9e4364f262f5
Revises: dcffabd05940
Create Date: 2025-03-03 08:54:27.202746

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e4364f262f5'
down_revision: Union[str, None] = 'dcffabd05940'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("posts") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer))
        batch_op.create_foreign_key("fk_posts_users", "users", ["user_id"], ["id"])

def downgrade():
    with op.batch_alter_table("posts") as batch_op:
        batch_op.drop_column("user_id")