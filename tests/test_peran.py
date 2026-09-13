"""Tangga peran, lingkup gudang, dan view — murni, tanpa basis data.

Satu tangga: operator < admin < superadmin. `staff`/`staf` adalah nama LAMA
yang masih ada di baris `users`; dibaca sebagai admin, tak pernah ditawarkan.
"""
from __future__ import annotations

from hmu_identitas import peran as P


def test_tangga_menurun_ke_bawah():
    assert P.admin_keatas(P.SUPERADMIN) and P.admin_keatas(P.ADMIN)
    assert not P.admin_keatas(P.OPERATOR)
    assert P.staf_keatas("staff") and P.staf_keatas("staf") and P.staf_keatas(P.ADMIN)
    assert not P.staf_keatas(P.OPERATOR) and not P.staf_keatas(None) and not P.staf_keatas("dewa")
    assert P.super_saja(" SuperAdmin ") and not P.super_saja(P.ADMIN)
    assert P.operator_saja("OPERATOR") and not P.operator_saja(P.ADMIN)


def test_tingkat_dan_langit_langit():
    assert P.tingkat(P.SUPERADMIN) > P.tingkat(P.ADMIN) > P.tingkat("staff") > P.tingkat(P.OPERATOR) > P.tingkat("")
    # Admin tak boleh mengangkat Super Admin; Super Admin boleh mengangkat siapa pun.
    assert P.terlalu_tinggi(P.ADMIN, P.SUPERADMIN)
    assert not P.terlalu_tinggi(P.SUPERADMIN, P.SUPERADMIN)
    assert not P.terlalu_tinggi(P.ADMIN, P.OPERATOR)


def test_peran_efektif_hanya_turun():
    assert P.peran_efektif(P.SUPERADMIN, "operator:g2") == P.OPERATOR
    assert P.peran_efektif(P.ADMIN, "superadmin") == P.ADMIN
    assert P.peran_efektif(P.OPERATOR, "admin") == P.OPERATOR
    assert P.peran_efektif(P.ADMIN, "") == P.ADMIN
    assert P.urai("operator:g1") == (P.OPERATOR, "g1")
    assert P.urai("operator:g9") == (P.OPERATOR, None)


def test_lingkup_gudang():
    assert P.lingkup(P.ADMIN, None) == P.SEMUA
    assert P.lingkup("staff", "Gudang 1 — Selepan") == P.SEMUA
    assert P.lingkup(P.OPERATOR, "Gudang 1 — Selepan") == P.G1
    assert P.lingkup(P.OPERATOR, "Gudang 2 — Penyosohan") == P.G2
    assert P.lingkup(P.OPERATOR, None) == P.TANPA
    assert P.lingkup("", "Gudang 1") == P.TANPA


def test_view_dari_peran_dan_lingkup():
    assert P.view(P.SUPERADMIN, P.SEMUA) == P.V_SUPER
    assert P.view(P.ADMIN, P.SEMUA) == P.V_ADMIN
    assert P.view("staf", P.SEMUA) == P.V_ADMIN
    assert P.view(P.OPERATOR, P.G1) == P.V_SELEPAN
    assert P.view(P.OPERATOR, P.G2) == P.V_POLESAN
    assert P.view(P.OPERATOR, P.TANPA) == P.V_TAMU
    assert P.VIEW_DARI_PERAN["staff"] == P.V_ADMIN
    assert set(P.VIEW_MEJA) == {P.V_SUPER, P.V_ADMIN}


def test_pemetaan_peran_timbangan_bolak_balik():
    assert P.ke_timbangan(P.OPERATOR) == "PETUGAS"
    assert P.ke_timbangan("staff") == "ADMIN"
    assert P.ke_timbangan(P.SUPERADMIN) == "SUPERADMIN"
    assert P.dari_timbangan("PETUGAS") == P.OPERATOR
    assert P.dari_timbangan("ADMIN") == P.ADMIN
    assert P.dari_timbangan("SUPERADMIN") == P.SUPERADMIN


def test_daftar_yang_ditawarkan_tanpa_nama_lama():
    assert [k for k, _ in P.PILIHAN] == [P.OPERATOR, P.ADMIN, P.SUPERADMIN]
    assert P.LABEL[P.SUPERADMIN] == "Super Admin"
