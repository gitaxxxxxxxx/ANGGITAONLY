import os
import django
from decimal import Decimal
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from kas_app.models import (
    ProfilOrganisasi, Divisi, Anggota,
    KategoriTransaksi, Transaksi, PeriodeKas, IuranKas, PengajuanIuran
)

def run_seed():
    print("🌱 Memulai seeding database SIMKAS ORMAWA...")

    # 1. Superuser / Admin
    user, created = User.objects.get_or_create(username='admin', defaults={
        'email': 'admin@ormawa.ac.id',
        'first_name': 'Bendahara',
        'last_name': 'Umum',
        'is_staff': True,
        'is_superuser': True
    })
    user.set_password('admin123')
    user.save()
    print("✅ User admin/admin123 siap.")

    # 2. Profil Organisasi
    profil, _ = ProfilOrganisasi.objects.get_or_create(
        id=1,
        defaults={
            'nama_organisasi': 'BEM Fakultas Ilmu Komputer',
            'nama_institusi': 'Universitas Indonesia',
            'singkatan': 'BEM FASILKOM',
            'periode_kepengurusan': '2026/2027',
            'nama_ketua': 'Muhammad Fikri Pratama',
            'nim_ketua': '2308101001',
            'nama_bendahara': 'Nabila Nur Azizah',
            'nim_bendahara': '2308101015',
            'nama_pembina': 'Dr. Eng. Ir. Bambang Hermanto, M.T.',
            'nip_pembina': '198205142006041002',
            'nominal_kas_wajib': Decimal('10000'),
            'periode_kas': 'bulanan',
            'saldo_awal': Decimal('750000'),
            'alamat_sekretariat': 'Gedung PKM Lt. 2 Kampus Terpadu, Jl. Lingkar Kampus No. 1',
            'email': 'bemfasilkom@univ.ac.id',
            'no_telepon': '081234567890'
        }
    )
    print("✅ Profil organisasi siap.")

    # 3. Divisi / Departemen
    divisi_data = [
        ('BPH', 'Badan Pengurus Harian', 'Pimpinan inti organisasi (Ketua, Sekretaris, Bendahara)'),
        ('PSDM', 'Pengembangan Sumber Daya Mahasiswa', 'Kaderisasi, upgrading, dan pelatihan internal ormawa'),
        ('KOMINFO', 'Komunikasi dan Informasi', 'Publikasi media sosial, dokumentasi, dan teknologi informasi'),
        ('KASTRAT', 'Kajian dan Aksi Strategis', 'Riset isu kemahasiswaan, sosial politik, dan advokasi'),
        ('DANUS', 'Dana dan Usaha', 'Penggalangan dana mandiri, merchandise, dan sponsorship'),
        ('SOSMA', 'Sosial Masyarakat', 'Pengabdian masyarakat, bakti sosial, dan aksi kemanusiaan'),
    ]
    divisi_dict = {}
    for kode, nama, ket in divisi_data:
        d, _ = Divisi.objects.get_or_create(kode=kode, defaults={'nama': nama, 'keterangan': ket})
        divisi_dict[kode] = d
    print(f"✅ {len(divisi_dict)} Divisi berhasil dibuat.")

    # 4. Kategori Transaksi
    kategori_masuk = [
        ('Iuran Kas Anggota', 'Penerimaan kas rutin wajib bulanan seluruh anggota', True),
        ('Dana Usaha (Danus)', 'Keuntungan penjualan merchandise, makanan, dan bazar ormawa', False),
        ('Sponsorship & Kemitraan', 'Dana sponsor dari perusahaan mitra untuk kegiatan ormawa', False),
        ('Subsidi Fakultas / Rektorat', 'Bantuan dana kemahasiswaan dari dekanat fakultas', False),
        ('Donasi Alumni & Simpatisan', 'Sumbangan sukarela dari ikatan alumni fakultas', False),
    ]
    kat_dict = {}
    for nama, desk, is_kas in kategori_masuk:
        k, _ = KategoriTransaksi.objects.get_or_create(
            nama=nama,
            jenis='masuk',
            defaults={'deskripsi': desk, 'is_iuran_kas': is_kas}
        )
        kat_dict[nama] = k

    kategori_keluar = [
        ('Program Kerja (Proker)', 'Biaya pelaksanaan kegiatan seminar, workshop, dies natalis'),
        ('Pengadaan ATK & Kesekretariatan', 'Kertas, map, tinta print, stempel, dan perlengkapan LPJ'),
        ('Konsumsi Rapat Koordinasi', 'Snack dan konsumsi rapat pleno dan musyawarah kerja'),
        ('Akomodasi & Transportasi', 'Biaya transportasi delegasi lomba dan kunjungan ormawa'),
        ('Pengembangan IT & Media Sosial', 'Sewa domain, hosting website ormawa, dan langganan Canva Pro'),
        ('Bakti Sosial & Aksi Lapangan', 'Pengeluaran bantuan sosial masyarakat dan kemanusiaan'),
    ]
    for nama, desk in kategori_keluar:
        k, _ = KategoriTransaksi.objects.get_or_create(
            nama=nama,
            jenis='keluar',
            defaults={'deskripsi': desk, 'is_iuran_kas': False}
        )
        kat_dict[nama] = k
    print("✅ Kategori transaksi berhasil dibuat.")

    # 5. Anggota Organisasi (4 Mahasiswa Sesuai Permintaan)
    # Hapus data anggota & user anggota lama agar database bersih
    Anggota.objects.all().delete()
    User.objects.filter(is_staff=False, is_superuser=False).delete()

    anggota_raw = [
        ('2401010262', 'Ni Made Anggita Maharani', 'BPH', 'Sekretaris', 2024, '081234567001'),
        ('2401010259', 'I Made Apriana', 'PSDM', 'Kepala Divisi', 2024, '081234567002'),
        ('2401010505', 'Ngurah Putra Amerta Widhi Gunaya', 'KOMINFO', 'Staff Media & IT', 2024, '081234567003'),
        ('2401010838', 'Novansius Marijo Lende', 'SOSMA', 'Staff Pengabdian', 2024, '081234567004'),
    ]

    # User alias demo role Anggota: anggota / anggota123
    user_anggota_demo, _ = User.objects.get_or_create(username='anggota', defaults={
        'first_name': 'Ni Made Anggita',
        'last_name': 'Maharani',
        'email': '2401010262@mahasiswa.univ.ac.id',
        'is_staff': False,
        'is_superuser': False
    })
    user_anggota_demo.set_password('anggota123')
    user_anggota_demo.save()

    anggota_objs = []
    for nim, nama, div_kode, jab, angk, hp in anggota_raw:
        # Buat user per mahasiswa dengan username = NIM dan password = NIM
        u_obj, _ = User.objects.get_or_create(username=nim, defaults={
            'first_name': nama.split()[0],
            'last_name': ' '.join(nama.split()[1:]),
            'email': f"{nim}@mahasiswa.univ.ac.id",
            'is_staff': False,
            'is_superuser': False
        })
        u_obj.set_password(nim)
        u_obj.save()

        ag, _ = Anggota.objects.get_or_create(
            nim=nim,
            defaults={
                'nama': nama,
                'divisi': divisi_dict[div_kode],
                'jabatan': jab,
                'angkatan': angk,
                'no_hp': hp,
                'email': f"{nim}@mahasiswa.univ.ac.id",
                'status_aktif': True,
                'tanggal_bergabung': date(2026, 1, 10),
                'user': u_obj
            }
        )
        if not ag.user:
            ag.user = u_obj
            ag.save()
        anggota_objs.append(ag)
    print(f"✅ {len(anggota_objs)} Anggota mahasiswa resmi berhasil didaftarkan dengan login NIM.")

    # 6. Periode Kas 2026 (Januari - Desember)
    bulan_list = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
    ]
    periode_objs = []
    for b_num, b_nama in bulan_list:
        p, _ = PeriodeKas.objects.get_or_create(
            bulan=b_num,
            tahun=2026,
            defaults={
                'nama_periode': f"{b_nama} 2026",
                'nominal': Decimal('10000'),
                'is_active': True
            }
        )
        periode_objs.append(p)
    print("✅ 12 Periode Kas 2026 berhasil dibuat.")

    # 7. Data Pembayaran Iuran Kas (Simulasi Realistic untuk 4 Mahasiswa)
    kat_iuran = kat_dict['Iuran Kas Anggota']

    # Delete existing transactions and iuran for fresh clean seeding
    Transaksi.objects.all().delete()
    IuranKas.objects.all().delete()

    for idx, ag in enumerate(anggota_objs):
        if idx == 0:
            lunas_sampai_bulan = 9  # Ni Made Anggita Maharani: Jan-Sep lunas (Okt menunggu verifikasi bukti)
        elif idx == 1:
            lunas_sampai_bulan = 10 # I Made Apriana: Jan-Okt lunas (Nov menunggu verifikasi bukti)
        elif idx == 2:
            lunas_sampai_bulan = 8  # Ngurah Putra Amerta Widhi Gunaya: Jan-Agt lunas
        else:
            lunas_sampai_bulan = 7  # Novansius Marijo Lende: Jan-Jul lunas

        for p in periode_objs:
            if p.bulan <= lunas_sampai_bulan:
                # Lunas
                tgl_bayar = date(2026, p.bulan, min(5 + idx, 28))
                trx = Transaksi.objects.create(
                    jenis='masuk',
                    kategori=kat_iuran,
                    nominal=p.nominal,
                    judul=f"Iuran Kas: {ag.nama} ({p.nama_periode})",
                    keterangan=f"Pembayaran kas rutin wajib bulan {p.nama_periode}",
                    tanggal=tgl_bayar,
                    divisi_terkait=ag.divisi,
                    dicatat_oleh=user
                )
                IuranKas.objects.create(
                    anggota=ag,
                    periode=p,
                    status='lunas',
                    nominal_dibayar=p.nominal,
                    tanggal_bayar=tgl_bayar,
                    metode_pembayaran='QRIS' if idx % 2 == 0 else 'Transfer Bank',
                    transaksi=trx
                )
            else:
                # Belum Lunas
                IuranKas.objects.create(
                    anggota=ag,
                    periode=p,
                    status='belum_lunas',
                    nominal_dibayar=Decimal('0')
                )
    print("✅ Seluruh data matriks iuran kas 4 anggota berhasil disinkronkan.")

    # 8. Transaksi Kas Masuk & Keluar Non-Iuran (Simulasi Operasional BEM 2026 - Data Kampus & Sponsorship)
    transaksi_sample = [
        # PEMASUKAN (Sponsorship, Dana Usaha Kampus, BOK Kemahasiswaan Dekanat, Donasi Alumni)
        ('masuk', 'Subsidi Fakultas / Rektorat', 3500000, 'Bantuan Operasional Kemahasiswaan (BOK) Dekanat Fasilkom Termin 1', date(2026, 1, 15), 'BPH', 'Pencairan dana alokasi ormawa semester genap dari Dekanat Fasilkom'),
        ('masuk', 'Dana Usaha (Danus)', 1250000, 'Dana Usaha: Pre-Order Kemeja PDH Resmi & Lanyard Ormawa', date(2026, 2, 10), 'DANUS', 'Keuntungan bersih penjualan seragam PDH angkatan baru dan gantungan kunci ormawa'),
        ('masuk', 'Sponsorship & Kemitraan', 4500000, 'Sponsorship PT Telkomsel - Dies Natalis Fasilkom & Hackathon 2026', date(2026, 3, 5), 'DANUS', 'Pencairan dana sponsor paket platinum PT Telkomsel Indonesia untuk event tahunan kampus'),
        ('masuk', 'Sponsorship & Kemitraan', 3000000, 'Sponsorship Bank Mandiri - Kemitraan Seminar FinTech & Karir Perbankan', date(2026, 3, 18), 'DANUS', 'Dana kemitraan edukasi perbankan digital dan literasi keuangan mahasiswa Fasilkom'),
        ('masuk', 'Dana Usaha (Danus)', 480000, 'Dana Usaha: Paid Promote Instagram Ormawa Dies Natalis', date(2026, 4, 2), 'KOMINFO', 'Laba jasa publikasi paid promote event eksternal di feed dan story official Instagram BEM'),
        ('masuk', 'Sponsorship & Kemitraan', 2500000, 'Sponsorship Dicoding Academy - Pelatihan Web & Sertifikasi Mahasiswa', date(2026, 5, 8), 'DANUS', 'Dukungan sponsor pelatihan developer web, voucher sertifikasi, dan merchandise peserta'),
        ('masuk', 'Donasi Alumni & Simpatisan', 1500000, 'Donasi Ikatan Alumni Fasilkom (ILUNI) untuk Kas Ormawa', date(2026, 5, 25), 'BPH', 'Sumbangan sukarela alumni angkatan 2018 untuk program kerja kemahasiswaan dan kas darurat'),
        ('masuk', 'Subsidi Fakultas / Rektorat', 3000000, 'Bantuan Operasional Kemahasiswaan (BOK) Dekanat Fasilkom Termin 2', date(2026, 8, 12), 'BPH', 'Pencairan subsidi operasional ormawa semester ganjil dari kas kemahasiswaan fakultas'),
        ('masuk', 'Sponsorship & Kemitraan', 2000000, 'Sponsorship PT Paragon Technology / Wardah Campus Roadshow', date(2026, 9, 14), 'DANUS', 'Sponsor seminar grooming, personal branding, and career development mahasiswa'),
        ('masuk', 'Dana Usaha (Danus)', 850000, 'Dana Usaha: Stand Bazar Makanan & Minuman Expo Kewirausahaan Kampus', date(2026, 10, 6), 'DANUS', 'Penjualan minuman kekinian, kopi cold brew, dan snack di festival expo ormawa kampus'),

        # PENGELUARAN (Operasional Kampus, Proker, Dies Natalis, ATK, Konsumsi Rapat)
        ('keluar', 'Pengadaan ATK & Kesekretariatan', 220000, 'Pengadaan Kertas A4, Map Berkas, dan Materai Pelantikan Pengurus', date(2026, 1, 18), 'BPH', 'Perlengkapan administrasi SK pelantikan dan arsip ormawa awal kepengurusan'),
        ('keluar', 'Konsumsi Rapat Koordinasi', 240000, 'Konsumsi Rapat Musyawarah Kerja (Muker) Awal Periode', date(2026, 1, 22), 'BPH', 'Snack dan makan siang 35 orang pengurus ormawa di ruang sidang kampus'),
        ('keluar', 'Pengembangan IT & Media Sosial', 450000, 'Perpanjangan Domain bemfasilkom.ac.id & Cloud Hosting Ormawa', date(2026, 2, 5), 'KOMINFO', 'Biaya server website resmi ormawa dan database kepengurusan selama 1 tahun'),
        ('keluar', 'Program Kerja (Proker)', 1850000, 'Pelaksanaan Latihan Dasar Kepemimpinan Mahasiswa (LDKM)', date(2026, 2, 28), 'PSDM', 'Honor narasumber materi kepemimpinan mahasiswa, sertifikat, dan modul latihan'),
        ('keluar', 'Program Kerja (Proker)', 2200000, 'Sewa Gedung Serbaguna (GSG) Kampus & Sound System Dies Natalis', date(2026, 3, 20), 'KOMINFO', 'Penyewaan venue acara seminar nasional dies natalis dan paket sound system 5000 watt'),
        ('keluar', 'Pengadaan ATK & Kesekretariatan', 380000, 'Cetak Spanduk Banner 4x2m & Backdrop Panggung Dies Natalis', date(2026, 3, 21), 'BPH', 'Digital printing spanduk sponsor Telkomsel/Mandiri dan backdrop panggung utama'),
        ('keluar', 'Konsumsi Rapat Koordinasi', 145000, 'Konsumsi Rapat Koordinasi Evaluasi Panitia Dies Natalis', date(2026, 4, 5), 'BPH', 'Konsumsi rapat pembubaran panitia dies natalis Fasilkom'),
        ('keluar', 'Bakti Sosial & Aksi Lapangan', 1250000, 'Penyaluran Paket Sembako Program Fasilkom Mengabdi di Desa Binaan', date(2026, 5, 20), 'SOSMA', 'Pengadaan 40 paket sembako untuk warga lingkar kampus binaan ormawa'),
        ('keluar', 'Akomodasi & Transportasi', 550000, 'Transportasi & Tiket Kereta Delegasi Kongres Mahasiswa Nasional', date(2026, 6, 15), 'KASTRAT', 'Biaya keberangkatan delegasi ketua dan sekjen ormawa ke forum nasional'),
        ('keluar', 'Program Kerja (Proker)', 1600000, 'Workshop Career Preparation & Talkshow Pemateri (Sponsor Dicoding)', date(2026, 7, 24), 'PSDM', 'Honorarium pembicara industri teknologi dan sertifikat peserta'),
        ('keluar', 'Pengadaan ATK & Kesekretariatan', 95000, 'Stempel Organisasi, Bak Tinta, & Tinta Cadangan', date(2026, 8, 10), 'BPH', 'Pembaruan stempel resmi BEM Fasilkom periode 2026/2027'),
        ('keluar', 'Pengembangan IT & Media Sosial', 150000, 'Langganan Akun Canva Pro Tim Medkom Ormawa (1 Tahun)', date(2026, 9, 2), 'KOMINFO', 'Akun tim desain untuk konten feed Instagram ormawa dan publikasi proker'),
        ('keluar', 'Program Kerja (Proker)', 1400000, 'Penyelenggaraan Diskusi Publik & Kajian Advokasi UKT Kampus', date(2026, 10, 14), 'KASTRAT', 'Konsumsi peserta dan narasumber forum advokasi kemahasiswaan Fasilkom'),
        ('keluar', 'Konsumsi Rapat Koordinasi', 160000, 'Konsumsi Rapat Pleno Koordinasi LPJ Akhir Tahun', date(2026, 11, 10), 'BPH', 'Snack rapat persiapan laporan pertanggungjawaban kepengurusan'),
        ('keluar', 'Pengadaan ATK & Kesekretariatan', 350000, 'Cetak Buku Hardcover Laporan Pertanggungjawaban (LPJ) Dekanat', date(2026, 11, 15), 'BPH', 'Jilid hardcover 5 eksemplar LPJ untuk arsip Dekanat Fasilkom dan Rektorat'),
    ]

    for jenis, kat_nama, nominal, judul, tgl, div_kode, ket in transaksi_sample:
        Transaksi.objects.create(
            jenis=jenis,
            kategori=kat_dict[kat_nama],
            nominal=Decimal(str(nominal)),
            judul=judul,
            tanggal=tgl,
            divisi_terkait=divisi_dict[div_kode],
            keterangan=ket,
            dicatat_oleh=user
        )
    print(f"✅ {len(transaksi_sample)} Transaksi operasional kas berhasil dicatat.")

    # 9. Sample Pengajuan Pembayaran Iuran dari Anggota (Menunggu Verifikasi Bendahara)
    PengajuanIuran.objects.all().delete()
    from kas_app.views import generate_mock_transfer_receipt

    ag_anggita = Anggota.objects.filter(nim='2401010262').first()
    p_okt = PeriodeKas.objects.filter(tahun=2026, bulan=10).first()
    if ag_anggita and p_okt:
        resi_anggita = generate_mock_transfer_receipt(
            ag_anggita, p_okt, metode='Transfer Bank BCA',
            catatan='Sudah transfer via m-BCA a.n. Ni Made Anggita Maharani'
        )
        PengajuanIuran.objects.create(
            anggota=ag_anggita,
            periode=p_okt,
            nominal=Decimal('10000'),
            metode_pembayaran='Transfer Bank',
            bukti_transfer=resi_anggita,
            catatan='Sudah transfer via Bank BCA a.n. Ni Made Anggita Maharani. Mohon verifikasinya min, terima kasih!',
            status='menunggu'
        )

    ag_apriana = Anggota.objects.filter(nim='2401010259').first()
    p_nov = PeriodeKas.objects.filter(tahun=2026, bulan=11).first()
    if ag_apriana and p_nov:
        resi_apriana = generate_mock_transfer_receipt(
            ag_apriana, p_nov, metode='QRIS',
            catatan='Scan QRIS resmi BEM a.n. I Made Apriana'
        )
        PengajuanIuran.objects.create(
            anggota=ag_apriana,
            periode=p_nov,
            nominal=Decimal('10000'),
            metode_pembayaran='QRIS',
            bukti_transfer=resi_apriana,
            catatan='Pembayaran kas bulan November via scan QRIS resmi ormawa.',
            status='menunggu'
        )
    print("✅ 2 Pengajuan iuran kas anggota (Lengkap dengan Bukti Resi Bank/QRIS) siap diverifikasi.")

    # Hitung Saldo Akhir
    total_in = Transaksi.objects.filter(jenis='masuk').aggregate(django.db.models.Sum('nominal'))['nominal__sum'] or Decimal('0')
    total_out = Transaksi.objects.filter(jenis='keluar').aggregate(django.db.models.Sum('nominal'))['nominal__sum'] or Decimal('0')
    saldo_akhir = profil.saldo_awal + total_in - total_out

    print("==================================================")
    print(f"✨ SEEDING DATABASE SELESAI!")
    print(f"💰 Saldo Awal: Rp {profil.saldo_awal:,.0f}")
    print(f"📈 Total Kas Masuk: Rp {total_in:,.0f}")
    print(f"📉 Total Kas Keluar: Rp {total_out:,.0f}")
    print(f"💎 Saldo Akhir Kas: Rp {saldo_akhir:,.0f}")
    print(f"👤 Login Bendahara : admin / admin123")
    print(f"👤 Login Anggota (Username = NIM, Password = NIM):")
    print(f"   - 2401010262 / 2401010262 : Ni Made Anggita Maharani")
    print(f"   - 2401010259 / 2401010259 : I Made Apriana")
    print(f"   - 2401010505 / 2401010505 : Ngurah Putra Amerta Widhi Gunaya")
    print(f"   - 2401010838 / 2401010838 : Novansius Marijo Lende")
    print("==================================================")

if __name__ == '__main__':
    run_seed()
