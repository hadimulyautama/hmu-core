# core — lapisan inti/master bersama

**Peran:** satu sumber kebenaran skema **master** yang dipakai SEMUA sistem
(Kantor, Produksi, Timbangan) sebagai **git submodule**.

## Isi (rencana)
- Model master: `User`, `Warehouse`, `Supplier`, `Pelanggan`, `Silo`, `Dryer`, `Heartbeat`
- `Base` / `TimestampMixin`
- Migrasi Alembic khusus tabel master — **`version_table` sendiri**, dijalankan **satu runner**
  (agar tak balapan antar sistem di DB yang sama).

## Prinsip
- Master (mis. `Supplier`/`Pelanggan`) = cermin master resmi; `Pelanggan` disinkron dari Kledo.
- Domain (batch, giling, SOP, approval, dst.) **BUKAN** di sini — itu milik repo masing-masing.

> Kosong sekarang. Diisi bertahap sesuai cetak-biru. Kode live masih di `../app` sampai migrasi.
