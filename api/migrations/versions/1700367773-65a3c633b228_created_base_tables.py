"""
Created base tables.

Revision ID: 65a3c633b228
Revises:
Create Date: 2023-11-18 20:22:53.663557

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "65a3c633b228"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "command_metrics",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=False),
        sa.Column("command_name", sa.String(), nullable=False),
        sa.Column("successfully_completed", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "trusted",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "warframe_items",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("thumb", sa.Text(), nullable=False),
        sa.Column("item_name", sa.Text(), nullable=False),
        sa.Column("url_name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "warframe_market_orders",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("item_name", sa.Text(), nullable=False),
        sa.Column("url_name", sa.Text(), nullable=False),
        sa.Column("order_type", sa.Text(), nullable=False),
        sa.Column("platinum", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "warframe_market_tracked_orders",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("platinum", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["warframe_items.id"],
        ),
        sa.PrimaryKeyConstraint("item_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("warframe_market_tracked_orders")
    op.drop_table("warframe_market_orders")
    op.drop_table("warframe_items")
    op.drop_table("trusted")
    op.drop_table("command_metrics")
    # ### end Alembic commands ###