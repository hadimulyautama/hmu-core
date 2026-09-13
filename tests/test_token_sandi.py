"""Sandi dan token sesi — sama untuk semua aplikasi."""
from __future__ import annotations

import time

import pytest

from hmu_identitas import sandi, token


def test_hash_dan_cek_sandi():
    h = sandi.hash_sandi("rahasia123")
    assert h.startswith("scrypt$")
    assert sandi.cek_sandi("rahasia123", h)
    assert not sandi.cek_sandi("salah", h)
    assert not sandi.cek_sandi("rahasia123", "bukan-hash")
    assert not sandi.cek_sandi("apa pun", sandi.HASH_TIRUAN)
    with pytest.raises(ValueError):
        sandi.hash_sandi("12345")


async def test_cek_sandi_async_sama_hasilnya():
    h = sandi.hash_sandi("rahasia123")
    assert await sandi.cek_sandi_async("rahasia123", h)
    assert not await sandi.cek_sandi_async("x", h)


def test_sandi_acak_tanpa_huruf_rancu():
    s = sandi.sandi_acak()
    assert len(s) == 10 and not set(s) & set("ilo01")


def test_token_bolak_balik_dan_versi():
    k = token.kunci_dari("rahasia-uji")
    t = token.buat_token(k, akun_id=7, versi=3, umur_detik=60, ekstra={"p": True})
    d = token.baca_token(k, t)
    assert d["akun_id"] == 7 and d["versi"] == 3 and d["p"] is True
    assert token.masih_berlaku(d, versi_akun=3)
    assert token.masih_berlaku(d, versi_akun=1)
    assert not token.masih_berlaku(d, versi_akun=4)
    assert token.baca_token(token.kunci_dari("kunci-lain"), t) is None


def test_token_tak_pernah_melempar():
    k = token.kunci_dari("rahasia-uji")
    for buruk in (None, "", "abc", "a.b", "é.ü", "x" * 5000, "eyJ.eyJ"):
        assert token.baca_token(k, buruk) is None
    kedaluwarsa = token.buat_token(k, akun_id=1, versi=1, umur_detik=-5)
    assert token.baca_token(k, kedaluwarsa) is None
    raksasa = token.buat_token(k, akun_id=2**40, versi=1, umur_detik=60)
    assert token.baca_token(k, raksasa) is None


def test_token_lama_tanpa_versi_dianggap_versi_satu():
    """Deploy tak boleh memutus semua orang: token yang belum membawa `v`
    dianggap versi 1, sama seperti yang berlaku di produksi dan timbangan."""
    import base64, hashlib, hmac, json
    k = token.kunci_dari("rahasia-uji")
    muatan = base64.urlsafe_b64encode(json.dumps(
        {"sub": 5, "exp": int(time.time()) + 60}).encode()).decode().rstrip("=")
    tanda = base64.urlsafe_b64encode(hmac.new(k, muatan.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    d = token.baca_token(k, f"{muatan}.{tanda}")
    assert d == {"akun_id": 5, "versi": 1, "exp": d["exp"]}
