"""Penjaga: peran tak disebut harfiah, dan paket ini tak menyeret SQLAlchemy
ke aplikasi tipis yang tak memilikinya."""
from __future__ import annotations

import subprocess
import sys

from hmu_identitas import penjaga


def test_pengintai_menangkap_bentuk_yang_dulu_lolos():
    contoh = [
        'if role == "superadmin": pass',
        'if "admin" == role: pass',
        'if user.role not in ("admin", "staff"): pass',
        'if role.startswith("admin"): pass',
        'u.role = "admin"',
        'if user.role in (\n    "admin",\n    "staff",\n): pass',
        'if user.role not in {"admin", "staff"}: pass',
        'if role != "admin": pass',
        'if akun.peran == "operator": pass',
        "if peran == 'PETUGAS': pass",
        'if saya.get("peran") not in ("superadmin", "admin", "staff", "staf"): pass',
        'if d["role"] == "admin": pass',
    ]
    for c in contoh:
        assert penjaga.peran_harfiah_dalam_teks(c, "contoh"), f"LOLOS: {c}"


def test_pengintai_tak_menuduh_pemakaian_yang_benar():
    for aman in (
        "if admin_keatas(user.role): pass",
        "if not staf_keatas(user.role): pass",
        'PERAN_STAF_KEATAS = ("superadmin", "admin", "staff")',
        "return role in PERAN_ADMIN_KEATAS",
        'return "admin" if "direksi" in roles else "staff"',
        "if user.role == P.OPERATOR: pass",
        'LABEL = {"admin": "Admin"}',
    ):
        assert not penjaga.peran_harfiah_dalam_teks(aman, "contoh"), aman


def test_import_paket_tak_menyeret_sqlalchemy():
    """Meja dan Gudang 2 tak memasang SQLAlchemy; `import hmu_identitas`
    harus tetap jalan di sana. Diuji di proses terpisah supaya bersih."""
    kode = ("import sys, hmu_identitas, hmu_identitas.peran, hmu_identitas.pintu, "
            "hmu_identitas.token, hmu_identitas.sandi; "
            "print('sqlalchemy' in sys.modules)")
    hasil = subprocess.run([sys.executable, "-c", kode], capture_output=True, text=True,
                           cwd=str(penjaga.AKAR_PAKET.parent))
    assert hasil.returncode == 0, hasil.stderr
    assert hasil.stdout.strip() == "False"


def test_manifest_bolak_balik(tmp_path):
    p = tmp_path / "hmu_identitas"
    p.mkdir()
    (p / "a.py").write_text("x = 1\n")
    penjaga.tulis_manifest(p)
    assert penjaga.baca_manifest(p) == penjaga.isi_manifest(p)
    (p / "a.py").write_text("x = 2\n")
    assert penjaga.baca_manifest(p) != penjaga.isi_manifest(p)
