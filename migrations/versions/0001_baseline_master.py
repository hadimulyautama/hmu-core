"""baseline master schema (core)

Tabel master bersama: warehouses, users, suppliers, pelanggan, silos, dryers.

PENTING — DB LIVE sudah punya tabel-tabel ini (dibuat chain migrasi lama repo produksi).
JANGAN jalankan upgrade di DB live; cukup tandai sudah-terpasang:
    DATABASE_URL=... alembic -c alembic.ini stamp 0001_baseline_master
upgrade() (create_table) hanya untuk DB BARU/dev. version_table = alembic_version_core.

Revision ID: 0001_baseline_master
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_baseline_master"
down_revision = None
branch_labels = None
depends_on = None


def _ts() -> tuple:
    """Kolom timestamp otomatis (fresh tiap tabel — Column tak bisa dipakai ulang)."""
    return (
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )


def upgrade() -> None:
    op.create_table(
        "warehouses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nama_gudang", sa.String(100), nullable=False),
        sa.Column("alamat", sa.Text),
        sa.Column("kapasitas_tumpuk_ton", sa.Numeric(10, 2)),
        sa.Column("kapasitas_tumpuk_pk_ton", sa.Numeric(10, 2)),
        *_ts(),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nama", sa.String(100), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("whatsapp_number", sa.String(30), unique=True),
        sa.Column("telegram_user_id", sa.BigInteger, unique=True),
        sa.Column("default_warehouse_id", sa.Integer, sa.ForeignKey("warehouses.id")),
        sa.Column("access_level", sa.String(20), nullable=False, server_default="operational"),
        sa.Column("wa_broadcast_opt_in", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(20), nullable=False, server_default="aktif"),
        *_ts(),
    )
    op.create_index("ix_users_telegram_user_id", "users", ["telegram_user_id"])
    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nama_supplier", sa.String(150), nullable=False),
        sa.Column("no_telfon", sa.String(30)),
        sa.Column("alamat", sa.Text),
        sa.Column("status", sa.String(20), nullable=False, server_default="aktif"),
        sa.Column("deleted_at", sa.DateTime()),
        sa.Column("kledo_contact_id", sa.BigInteger),
        *_ts(),
    )
    op.create_index("ix_suppliers_kledo_contact_id", "suppliers", ["kledo_contact_id"])
    op.create_table(
        "pelanggan",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nama_pelanggan", sa.String(150), nullable=False),
        sa.Column("no_telfon", sa.String(30)),
        sa.Column("alamat", sa.Text),
        sa.Column("status", sa.String(20), nullable=False, server_default="aktif"),
        sa.Column("deleted_at", sa.DateTime()),
        sa.Column("kledo_contact_id", sa.BigInteger),
        *_ts(),
    )
    op.create_index("ix_pelanggan_kledo_contact_id", "pelanggan", ["kledo_contact_id"])
    op.create_table(
        "silos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("warehouse_id", sa.Integer, sa.ForeignKey("warehouses.id"), nullable=False),
        sa.Column("nama_silo", sa.String(50), nullable=False),
        sa.Column("kapasitas_ton", sa.Numeric(10, 2)),
        sa.Column("status", sa.String(20), nullable=False, server_default="kosong"),
        *_ts(),
    )
    op.create_table(
        "dryers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("warehouse_id", sa.Integer, sa.ForeignKey("warehouses.id"), nullable=False),
        sa.Column("nama", sa.String(50), nullable=False),
        sa.Column("kapasitas_kg", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="aktif"),
        *_ts(),
    )


def downgrade() -> None:
    op.drop_table("dryers")
    op.drop_table("silos")
    op.drop_index("ix_pelanggan_kledo_contact_id", table_name="pelanggan")
    op.drop_table("pelanggan")
    op.drop_index("ix_suppliers_kledo_contact_id", table_name="suppliers")
    op.drop_table("suppliers")
    op.drop_index("ix_users_telegram_user_id", table_name="users")
    op.drop_table("users")
    op.drop_table("warehouses")
