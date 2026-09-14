"""Pensiunkan peran lama `staff`/`staf` — keputusan pemilik 15 September 2026.

Peran itu berdiri di dua sisi sekaligus (QA P4-03): melihat uang dan Meja,
tetapi ditolak aksi gudang. Tangga kini operator < admin < superadmin saja.
Baris `users` yang masih menyebut nama lama dipetakan ke `admin` — hak yang
paling dekat dengan yang selama ini dipegangnya. Di pabrik saat migrasi ini
ditulis: NOL baris (diperiksa 14 September 2026), jadi ini pagar, bukan
pemindahan. `users` dibaca kelima aplikasi; nilainya saja yang berubah,
bentuknya tidak.

Revision ID: 0002_pensiun_staff
Revises: 0001_baseline_master
"""
from alembic import op

revision = "0002_pensiun_staff"
down_revision = "0001_baseline_master"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE users SET role = 'admin' WHERE lower(role) IN ('staff', 'staf')")


def downgrade() -> None:
    # Nama lama tak dikembalikan: tak ada yang tahu baris mana yang dulu staff.
    pass
