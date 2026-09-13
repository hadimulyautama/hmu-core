"""Uji identitas di Postgres sungguhan.

Berjalan HANYA bila `UJI_PG_URL` disetel (loopback, nama basis data `uji_*`).
Skema dibangun dari metadata `hmu_core` + `hmu_identitas`: tabel `users` dan
`produksi_akun` — persis dua tabel yang dipakai paket ini.

    UJI_PG_URL=postgresql+asyncpg://postgres:uji@127.0.0.1:55434/uji_identitas \\
        ../produksi/.venv/bin/python -m pytest -q tests/pg
"""
from __future__ import annotations

import os

import pytest
import pytest_asyncio


def _url() -> str | None:
    url = os.environ.get("UJI_PG_URL", "").strip()
    if not url:
        return None
    if not ("127.0.0.1" in url or "localhost" in url):
        pytest.fail(f"UJI_PG_URL bukan loopback: {url.rsplit('@', 1)[-1]}")
    nama = url.rsplit("/", 1)[-1].split("?")[0]
    if not nama.startswith("uji_"):
        pytest.fail(f"nama basis data uji wajib berawalan 'uji_', bukan '{nama}'")
    return url


@pytest_asyncio.fixture
async def pg():
    url = _url()
    if url is None:
        pytest.skip("UJI_PG_URL kosong — uji Postgres dilewati")
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    import hmu_identitas.model  # noqa: F401
    from hmu_core import Base

    mesin = create_async_engine(url)
    async with mesin.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Sesi = async_sessionmaker(mesin, expire_on_commit=False)
    try:
        yield Sesi
    finally:
        async with mesin.begin() as conn:
            await conn.execute(text("TRUNCATE TABLE produksi_akun, users RESTART IDENTITY CASCADE"))
        await mesin.dispose()
