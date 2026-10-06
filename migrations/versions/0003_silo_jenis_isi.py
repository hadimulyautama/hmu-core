"""silos.jenis_isi ('pk' / 'broken') — keputusan pemilik 6 Oktober 2026

Broken (PK yang sudah disosoh, patah) dapat silonya sendiri sehingga jenis
bahan sebuah proses sosoh bisa diturunkan dari silo sumbernya — bukan
dicatat per-pemakaian. Lihat docstring `hmu_core.models.Silo`.

PENTING — seperti 0001_baseline_master: DB LIVE dan `uji_produksi` membangun
tabel `silos` lewat chain migrasi LAMA repo produksi (pelari belum
dipindahkan ke sini — "tahap kecil sendiri", CLAUDE.md), dan kolom ini sudah
ditambahkan di sana (`produksi/migrations/versions/0071_silo_jenis_isi.py`).
JANGAN jalankan upgrade chain ini di DB yang sudah dimigrasikan produksi;
tandai sudah-terpasang:
    DATABASE_URL=... alembic -c alembic.ini stamp 0003_silo_jenis_isi
upgrade() (add_column) hanya untuk DB BARU/dev yang skemanya dibangun dari
chain core ini sendiri sejak awal.

Revision ID: 0003_silo_jenis_isi
Revises: 0002_pensiun_staff
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_silo_jenis_isi"
down_revision = "0002_pensiun_staff"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "silos",
        sa.Column("jenis_isi", sa.String(20), nullable=False, server_default="pk"),
    )


def downgrade() -> None:
    op.drop_column("silos", "jenis_isi")
