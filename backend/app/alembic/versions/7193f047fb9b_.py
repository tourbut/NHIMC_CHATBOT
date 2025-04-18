"""empty message

Revision ID: 7193f047fb9b
Revises: 271b7bf67381
Create Date: 2024-11-21 14:41:40.989852

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import sqlmodel



# revision identifiers, used by Alembic.
revision: str = '7193f047fb9b'
down_revision: Union[str, None] = '271b7bf67381'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('dept_llm_id', sqlmodel.sql.sqltypes.GUID(), nullable=True))
    op.alter_column('chats', 'user_llm_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.create_foreign_key(None, 'chats', 'deptllm', ['dept_llm_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'chats', type_='foreignkey')
    op.alter_column('chats', 'user_llm_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.drop_column('chats', 'dept_llm_id')
    # ### end Alembic commands ###
