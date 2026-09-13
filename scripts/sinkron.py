#!/usr/bin/env python3
"""Vendor paket bersama ke repo aplikasi, lalu tulis manifest-nya.

    python scripts/sinkron.py ../produksi ../timbangan ../meja ../gudang2 ../kantor
    python scripts/sinkron.py --core ../produksi ../timbangan   # ikut hmu_core

`hmu_identitas` selalu disalin. `hmu_core` hanya dengan `--core` — kantor
memuatnya dari submodule `core/`, jadi tak boleh punya salinan kedua.
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
