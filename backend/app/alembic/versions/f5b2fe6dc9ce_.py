"""empty message

Revision ID: f5b2fe6dc9ce
Revises: 7b50f9cff550
Create Date: 2025-02-14 13:25:29.621792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import sqlmodel



# revision identifiers, used by Alembic.
revision: str = 'f5b2fe6dc9ce'
down_revision: Union[str, None] = '7b50f9cff550'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column('chats', sa.Column('chatbot_id', sqlmodel.sql.sqltypes.GUID(), nullable=True))
    op.create_foreign_key(None, 'chats', 'chatbot', ['chatbot_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'chats', type_='foreignkey')
    op.drop_column('chats', 'chatbot_id')


    # ### end Alembic commands ###
