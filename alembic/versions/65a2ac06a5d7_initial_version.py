"""Initial version

Revision ID: 65a2ac06a5d7
Revises:
Create Date: 2023-10-26 17:00:55.631589

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "65a2ac06a5d7"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "later_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("link", sa.String(length=500), nullable=False),
        sa.Column("tag", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("later_links")
    # ### end Alembic commands ###