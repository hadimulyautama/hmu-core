# core — paket bersama `hmu_core` & `hmu_identitas`

Bahasa Indonesia untuk kode, komentar, uji, dan pesan commit.

- `hmu_core`: skema master (users, suppliers, pelanggan, warehouses, silos,
  dryers). Pemilik skema & pelari migrasinya **core** (keputusan pemilik
  13 Sep 2026); pemindahan pelari dari produksi ke sini = tahap kecil sendiri.
- `hmu_identitas`: identitas bersama (lihat README). `__init__` HANYA memuat
  modul murni — Meja & Gudang 2 tak memasang SQLAlchemy; ada uji yang
  menjaganya.
- Mengubah paket = ubah DI SINI, naikkan `VERSI` bila perlu, lalu
  `python scripts/sinkron.py [--core] ../produksi ../timbangan ../meja
  ../gudang2 ../kantor`. Jangan sunting salinan vendored di repo lain.
- Peran tak pernah disebut harfiah; `penjaga.peran_harfiah` dipakai uji
  kelima repo. Menambah bentuk yang lolos = tambah contohnya di
  `tests/test_penjaga.py` dulu.
- Uji: pakai venv produksi (`../produksi/.venv/bin/python -m pytest -q tests`);
  Postgres dengan `UJI_PG_URL` loopback bernama `uji_*`.
- Jangan push, jangan deploy, jangan membaca nilai variabel Railway.
