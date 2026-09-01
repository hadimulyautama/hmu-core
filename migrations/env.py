"""Alembic env untuk core (tabel MASTER) — ASYNC (asyncpg), mengikuti pola env utama.

Berbagi DB dengan produksi & kantor, tapi memakai version_table SENDIRI
(`alembic_version_core`) sehingga tiap chain hanya menyentuh tabelnya sendiri.
URL dari env DATABASE_URL; dipastikan driver asyncpg + buang `sslmode` (tak dikenal asyncpg).
"""
from __future__ import annotations

import asyncio
import os
import re
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from hmu_core.base import Base
import hmu_core.models  # noqa: F401  — daftarkan semua tabel master ke metadata

config = context.config

VERSION_TABLE = "alembic_version_core"


def _db_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL belum diset untuk migrasi core.")
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]
    # asyncpg pakai param 'ssl', bukan 'sslmode' (punya psycopg2/libpq) — buang.
    url = re.sub(r"[?&]sslmode=[^&]*", "", url)
    return url


config.set_main_option("sqlalchemy.url", _db_url())

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table=VERSION_TABLE,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_offline() -> None:
    context.configure(
        url=_db_url(),
        target_metadata=target_metadata,
        version_table=VERSION_TABLE,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_async_migrations())
