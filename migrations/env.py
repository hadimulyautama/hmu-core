"""Alembic env untuk core (tabel MASTER).

Berbagi DB dengan produksi & kantor, tapi memakai version_table SENDIRI
(`alembic_version_core`) sehingga tiap chain hanya menyentuh tabelnya sendiri.
URL diambil dari env DATABASE_URL; driver async diubah ke sinkron untuk Alembic.
"""
from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from hmu_core.base import Base
import hmu_core.models  # noqa: F401  — daftarkan semua tabel master ke metadata

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
VERSION_TABLE = "alembic_version_core"


def _db_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL belum diset untuk migrasi core.")
    # Alembic berjalan SINKRON — buang driver async.
    return (
        url.replace("postgresql+asyncpg://", "postgresql://")
        .replace("postgres://", "postgresql://")
    )


def run_migrations_offline() -> None:
    context.configure(
        url=_db_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        version_table=VERSION_TABLE,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section) or {}
    section["sqlalchemy.url"] = _db_url()
    connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table=VERSION_TABLE,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
