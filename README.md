# core — lapisan inti/master bersama

**Peran:** satu sumber kebenaran skema **master** (`hmu_core`) dan
**identitas** (`hmu_identitas`) yang dipakai SEMUA sistem.

## `hmu_identitas` — satu orang, satu akun, satu sesi, satu saklar (Tahap 2, 13 Sep 2026)

Dipakai produksi, timbangan, gudang2, meja, kantor. Di-vendor utuh oleh
`scripts/sinkron.py` (`--core` ikut menyalin `hmu_core`), dijaga
`MANIFEST.sha256` + uji `tests/test_identitas_paket.py` di tiap repo.

| Modul | Isi | Butuh SQLAlchemy |
|---|---|---|
| `peran` | tangga operator·admin·superadmin, `TINGKAT`, `terlalu_tinggi`, lingkup gudang, view, pemetaan peran timbangan | tidak |
| `pintu` | `boleh_masuk(peran, aplikasi, lingkup)` — tabel pintu per aplikasi (keputusan pemilik) | tidak |
| `sandi`, `token` | scrypt & token HMAC berversi — bentuk sama untuk semua app, kunci per app | tidak |
| `model` | `Akun` = tabel `produksi_akun` (nama tabel tak diganti; chain migrasi masih produksi) | ya |
| `masuk` | `periksa_kredensial`, `akun_aktif` (pintu tiap permintaan), `naikkan_versi`, `ganti_sandi`, `nonaktifkan` (SATU saklar), `ada_superadmin_aktif` | ya |
| `penjaga` | manifest, pemeriksa AST "peran harfiah", "definisi ganda" | tidak |

Uji: `../produksi/.venv/bin/python -m pytest -q tests` (murni) dan dengan
`UJI_PG_URL=postgresql+asyncpg://…/uji_identitas` untuk `tests/pg`.

## Isi (rencana)
- Model master: `User`, `Warehouse`, `Supplier`, `Pelanggan`, `Silo`, `Dryer`, `Heartbeat`
- `Base` / `TimestampMixin`
- Migrasi Alembic khusus tabel master — **`version_table` sendiri**, dijalankan **satu runner**
  (agar tak balapan antar sistem di DB yang sama).

## Status
- ✅ Paket `hmu_core` dibangun: `Base`, `TimestampMixin`, 6 model master (diekstrak setia dari
  `app/models/master.py`). Import: `from hmu_core import User, Supplier, Pelanggan, Warehouse, Silo, Dryer`.
- ✅ Alembic core: `version_table = alembic_version_core` (terpisah dari produksi/kantor), baseline
  `0001_baseline_master`.
- ⏳ Belum: dijadikan **git submodule** di produksi/kantor/timbangan; belum di-`stamp` ke DB live.

## Cara pakai (nanti)
```bash
pip install -e ./core                      # atau tambahkan sebagai git submodule
# DB LIVE (tabel master sudah ada) — cukup tandai, JANGAN upgrade:
cd core && DATABASE_URL=... alembic -c alembic.ini stamp 0001_baseline_master
```

## Validasi vs DB live (2026-09-01, read-only)
Ke-6 tabel ada; **semua kolom cocok nama & tipe; server-default cocok.** Satu-satunya beda:
`status`/`access_level`/`wa_broadcast_opt_in` di **4 tabel lama** (`suppliers`, `users`, `silos`,
`dryers`) **NULLABLE** di DB, padahal model (benar) = NOT NULL. `pelanggan` (tabel baru) sudah
NOT NULL. Ini **drift legacy** — dikonfirmasi **0 baris NULL** (dari 181 supplier, dst.), jadi
**aman**: model `core` sengaja dijaga NOT NULL (skema yang benar). Opsional nanti: migrasi core
`0002` `ALTER COLUMN ... SET NOT NULL` untuk merapikan 4 tabel lama (pasti sukses, tak ada NULL).
`alembic stamp 0001` di DB live tetap valid.

## Prinsip
- Master (`Supplier`/`Pelanggan`) = cermin master resmi; `Pelanggan` disinkron dari Kledo.
- Domain (batch, giling, SOP, approval, dst.) **BUKAN** di sini — milik repo masing-masing.
- Skema HARUS identik dengan DB live — verifikasi sebelum `stamp`/deploy.

> Kode live masih di `../app` sampai migrasi Fase A selesai. Ini fondasi yang dipakai semua repo.
