"""Pintu per aplikasi — keputusan pemilik 13 September 2026.

operator → aplikasi operator (Gudang 2, Pos Produksi); admin → Meja;
timbangan → operator dan admin; superadmin → semua. Pos Produksi masih
menerima admin sampai Meja dipakai sungguhan (catatan di modul).
"""
from __future__ import annotations

from hmu_identitas import peran as P
from hmu_identitas import pintu


def test_superadmin_masuk_semua():
    for a in pintu.SEMUA_APLIKASI:
        assert pintu.boleh_masuk(P.SUPERADMIN, a), a


def test_admin_hanya_meja_timbangan_kantor_dan_pos_produksi():
    assert pintu.boleh_masuk(P.ADMIN, pintu.MEJA)
    assert pintu.boleh_masuk("staff", pintu.MEJA)
    assert pintu.boleh_masuk(P.ADMIN, pintu.TIMBANGAN)
    assert pintu.boleh_masuk(P.ADMIN, pintu.KANTOR)
    assert pintu.boleh_masuk(P.ADMIN, pintu.PRODUKSI)
    assert not pintu.boleh_masuk(P.ADMIN, pintu.GUDANG2)


def test_operator_hanya_aplikasi_operator_dan_timbangan():
    """Operator saling menggantikan (pemilik 13 Sep): gudang utamanya bukan
    pagar — operator Gudang 1 boleh masuk aplikasi Gudang 2, dan sebaliknya."""
    assert pintu.boleh_masuk(P.OPERATOR, pintu.GUDANG2, lingkup=P.G2)
    assert pintu.boleh_masuk(P.OPERATOR, pintu.GUDANG2, lingkup=P.G1)
    assert pintu.boleh_masuk(P.OPERATOR, pintu.GUDANG2, lingkup=P.TANPA)
    assert pintu.boleh_masuk(P.OPERATOR, pintu.PRODUKSI, lingkup=P.G1)
    assert pintu.boleh_masuk(P.OPERATOR, pintu.TIMBANGAN)
    assert not pintu.boleh_masuk(P.OPERATOR, pintu.MEJA)
    assert not pintu.boleh_masuk(P.OPERATOR, pintu.KANTOR)


def test_peran_tak_dikenal_ditolak_dan_pesannya_menyebut_aplikasi():
    assert not pintu.boleh_masuk("", pintu.MEJA)
    assert not pintu.boleh_masuk("dewa", pintu.TIMBANGAN)
    pesan = pintu.sebab_tolak(P.OPERATOR, pintu.MEJA)
    assert pesan and "operator" in pesan.lower()
    assert pintu.sebab_tolak(P.ADMIN, pintu.MEJA) is None
    assert pintu.sebab_tolak(P.OPERATOR, pintu.GUDANG2, lingkup=P.G1) is None
