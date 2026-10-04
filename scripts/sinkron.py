#!/usr/bin/env python3
"""Vendor paket bersama ke repo aplikasi, lalu tulis manifest-nya.

    python scripts/sinkron.py ../produksi ../timbangan ../kantor
    python scripts/sinkron.py --core ../produksi ../timbangan ../kantor   # ikut hmu_core

`hmu_identitas` selalu disalin. `hmu_core` hanya dengan `--core`.

Kantor dulu memuat `hmu_core` dari submodule `core/`, tapi submodule itu
DIBUANG 13 September 2026 malam (build GitHub di Railway tidak membawa isi
submodule, deploy gagal di `COPY core/hmu_core`) — sejak itu kantor
memvendor `hmu_core` persis seperti produksi dan timbangan, lewat skrip ini
dengan `--core`. Lupa menyertakan kantor berarti salinannya diam-diam
tertinggal dari produksi/timbangan (begitulah `kledo_kontak.py` bisa
berbeda aturan `type_id` di satu sistem tanpa disadari) — ikut sertakan
kantor setiap kali memakai `--core`.
Folder tujuan DIGANTI utuh, supaya tak ada salinan yang "hampir sama".
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AKAR))
from hmu_identitas import penjaga  # noqa: E402


def salin(paket: str, repo: Path) -> None:
    sumber = AKAR / paket
    penjaga.tulis_manifest(sumber)
    vend = repo / paket
    if vend.exists():
        shutil.rmtree(vend)
    shutil.copytree(sumber, vend, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    sisa = penjaga.vendor_selaras(repo, paket)
    print(f"{repo.name}/{paket}: {'selaras' if not sisa else sisa}")


def main(argv: list[str]) -> None:
    ikut_core = "--core" in argv
    tujuan = [a for a in argv if not a.startswith("--")]
    if not tujuan:
        sys.exit("pakai: sinkron.py [--core] <repo> [<repo> ...]")
    for t in tujuan:
        repo = Path(t).resolve()
        salin("hmu_identitas", repo)
        if ikut_core:
            salin("hmu_core", repo)


if __name__ == "__main__":
    main(sys.argv[1:])
