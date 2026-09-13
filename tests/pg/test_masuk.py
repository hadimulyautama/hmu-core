"""SATU fungsi "boleh masuk?" untuk semua aplikasi — diuji di Postgres.

Yang dijaga (QA X-11, P-S-05, T-19): kredensial diperiksa dengan waktu
jawab yang sama untuk nama yang tak ada; sesi hidup hanya bila versi token
masih sepadan DAN orangnya aktif di `users`; menonaktifkan = satu saklar
yang memutus sesi pada permintaan berikutnya; tak pernah ada keadaan
"tak ada Super Admin aktif" yang diciptakan diam-diam.
"""
from __future__ import annotations

import pytest

from hmu_identitas import masuk, peran as P, sandi
from hmu_identitas.model import Akun
from hmu_core import User


async def _orang(pg, *, nama="Budi", role=P.OPERATOR, username="budi", sandi_="rahasia123",
                 status="aktif", mode="bersama") -> int:
    async with pg() as db:
        u = User(nama=nama, role=role, status="aktif")
        db.add(u)
        await db.flush()
        a = Akun(user_id=u.id, username=username, password_hash=sandi.hash_sandi(sandi_),
                 status=status, mode_perangkat=mode)
        db.add(a)
        await db.commit()
        return a.id


async def test_kredensial_benar_mengembalikan_akun_dengan_orangnya(pg):
    aid = await _orang(pg)
    async with pg() as db:
        a = await masuk.periksa_kredensial(db, "Budi ", "rahasia123")
        assert a.id == aid and a.peran == P.OPERATOR and a.nama == "Budi"
        assert a.sesi_pendek is True and a.is_admin is False


async def test_nama_tak_ada_dan_sandi_salah_ditolak_dengan_pesan_yang_sama(pg):
    await _orang(pg)
    async with pg() as db:
        with pytest.raises(masuk.Tolak) as e1:
            await masuk.periksa_kredensial(db, "tidakada", "rahasia123")
        with pytest.raises(masuk.Tolak) as e2:
            await masuk.periksa_kredensial(db, "budi", "salah")
    assert e1.value.pesan == e2.value.pesan and e1.value.kode == 401 == e2.value.kode


async def test_nonaktif_di_master_menolak_walau_sandi_benar(pg):
    aid = await _orang(pg)
    async with pg() as db:
        (await db.get(Akun, aid)).user.status = "nonaktif"
        await db.commit()
    async with pg() as db:
        with pytest.raises(masuk.Tolak) as e:
            await masuk.periksa_kredensial(db, "budi", "rahasia123")
    assert e.value.kode == 403


async def test_sesi_hidup_lalu_putus_saat_versi_naik(pg):
    aid = await _orang(pg)
    async with pg() as db:
        assert await masuk.akun_aktif(db, aid, 1) is not None
        await masuk.naikkan_versi(db, aid)
    async with pg() as db:
        assert await masuk.akun_aktif(db, aid, 1) is None
        assert await masuk.akun_aktif(db, aid, 2) is not None


async def test_satu_saklar_nonaktif_memutus_pada_permintaan_berikutnya(pg):
    aid = await _orang(pg)
    async with pg() as db:
        akun = await masuk.akun_aktif(db, aid, 1)
        assert akun is not None
        await masuk.nonaktifkan(db, akun.user_id)
    async with pg() as db:
        # Versi apa pun — orangnya sudah tak bekerja di sini.
        assert await masuk.akun_aktif(db, aid, 1) is None
        assert await masuk.akun_aktif(db, aid, 99) is None
        u = await db.get(User, akun.user_id)
        a = await db.get(Akun, aid)
        assert u.status == "nonaktif" and a.status == "nonaktif"
    async with pg() as db:
        await masuk.nonaktifkan(db, akun.user_id, aktif=True)
    async with pg() as db:
        assert await masuk.akun_aktif(db, aid, a.token_version) is not None


async def test_menonaktifkan_superadmin_terakhir_ditolak(pg):
    aid = await _orang(pg, nama="Bos", role=P.SUPERADMIN, username="bos")
    async with pg() as db:
        assert await masuk.ada_superadmin_aktif(db)
        a = await db.get(Akun, aid)
        with pytest.raises(masuk.Tolak):
            await masuk.nonaktifkan(db, a.user_id)
    async with pg() as db:
        assert await masuk.ada_superadmin_aktif(db)


async def test_ganti_sandi_memutus_sesi_lama(pg):
    aid = await _orang(pg)
    async with pg() as db:
        a = await db.get(Akun, aid)
        with pytest.raises(masuk.Tolak):
            await masuk.ganti_sandi(db, a, sandi_lama="salah", sandi_baru="barubaru1")
        versi = await masuk.ganti_sandi(db, a, sandi_lama="rahasia123", sandi_baru="barubaru1")
    async with pg() as db:
        assert await masuk.akun_aktif(db, aid, 1) is None
        assert (await masuk.akun_aktif(db, aid, versi)) is not None
        assert (await masuk.periksa_kredensial(db, "budi", "barubaru1")).id == aid
