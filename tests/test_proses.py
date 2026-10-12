from datetime import datetime, timezone
from decimal import Decimal

import pytest

from hmu_core import (
    ArusProses, JenisPemilik, JenisProses, PemilikProses, Produk,
    ProsesOperasional, StatusProses, buat_produk,
)


def test_model_proses_menggabungkan_identitas_dan_arus_komoditas():
    padi = buat_produk("gabah", kondisi="kering")
    pk = buat_produk("beras_pk")
    proses = ProsesOperasional(
        aplikasi="produksi", id=12, kode="GIL-20261012-01",
        jenis=JenisProses.PENGGILINGAN, status=StatusProses.SELESAI,
        pemilik=PemilikProses(JenisPemilik.PABRIK),
        waktu_mulai=datetime(2026, 10, 12, 7, tzinfo=timezone.utc),
        waktu_selesai=datetime(2026, 10, 12, 9, tzinfo=timezone.utc),
        bahan=(ArusProses(padi, Decimal("1000"), "GB-01", 2),),
        hasil=(ArusProses(pk, Decimal("650"), "PK-01", 4),),
    )

    assert proses.jenis is JenisProses.PENGGILINGAN
    assert proses.bahan[0].produk.komoditas == "gabah"
    assert proses.hasil[0].produk.komoditas == "beras_pk"
    assert proses.referensi_asal == ()


def test_kontrak_proses_bisa_dipertukarkan_antar_aplikasi():
    proses = ProsesOperasional(
        aplikasi="produksi", id=12, kode="GIL-20261012-01",
        jenis=JenisProses.PENGGILINGAN, status=StatusProses.SELESAI,
        pemilik=PemilikProses(JenisPemilik.JASA, id=7, nama="Pak A"),
        bahan=(ArusProses(buat_produk("gabah", kondisi="kering"),
                          Decimal("1000.00"), "GB-01", 2),),
        hasil=(ArusProses(buat_produk("beras_pk"), Decimal("650.00"), "PK-01", 4),),
        referensi_asal=("GB-01",),
    )

    salinan = ProsesOperasional.dari_dict(proses.ke_dict())
    assert salinan == proses


def test_pemilik_jasa_memerlukan_identitas():
    with pytest.raises(ValueError, match="harus memiliki id"):
        PemilikProses(JenisPemilik.JASA)


def test_waktu_proses_tidak_boleh_terbalik():
    with pytest.raises(ValueError, match="sebelum waktu mulai"):
        ProsesOperasional(
            aplikasi="produksi", id=1, kode="POL-01",
            jenis=JenisProses.PENYOSOHAN, status=StatusProses.SELESAI,
            pemilik=PemilikProses(JenisPemilik.PABRIK),
            waktu_mulai=datetime(2026, 10, 12, 9),
            waktu_selesai=datetime(2026, 10, 12, 8),
        )


def test_arus_proses_menolak_berat_negatif():
    with pytest.raises(ValueError, match="tidak boleh negatif"):
        ArusProses(Produk("beras_pk", {}), Decimal("-1"))
