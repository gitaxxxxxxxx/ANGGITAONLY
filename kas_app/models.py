import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class ProfilOrganisasi(models.Model):
    PERIODE_KAS_CHOICES = [
        ('bulanan', 'Bulanan'),
        ('mingguan', 'Mingguan'),
    ]

    nama_organisasi = models.CharField(max_length=150, default='BEM Fakultas Ilmu Komputer')
    nama_institusi = models.CharField(max_length=150, default='Universitas Indonesia')
    singkatan = models.CharField(max_length=50, default='BEM FASILKOM')
    periode_kepengurusan = models.CharField(max_length=50, default='2026/2027')
    nama_ketua = models.CharField(max_length=150, default='Muhammad Fikri Pratama')
    nim_ketua = models.CharField(max_length=30, default='2308101001')
    nama_bendahara = models.CharField(max_length=150, default='Nabila Nur Azizah')
    nim_bendahara = models.CharField(max_length=30, default='2308101015')
    nama_pembina = models.CharField(max_length=150, default='Dr. Eng. Ir. Bambang Hermanto, M.T.')
    nip_pembina = models.CharField(max_length=50, default='198205142006041002')
    nominal_kas_wajib = models.DecimalField(max_digits=12, decimal_places=2, default=10000)
    periode_kas = models.CharField(max_length=20, choices=PERIODE_KAS_CHOICES, default='bulanan')
    saldo_awal = models.DecimalField(max_digits=15, decimal_places=2, default=500000)
    logo = models.ImageField(upload_to='logo/', blank=True, null=True)
    alamat_sekretariat = models.TextField(default='Gedung PKM Lt. 2 Kampus Terpadu, Jl. Lingkar Kampus No. 1')
    email = models.EmailField(default='bemfasilkom@univ.ac.id')
    no_telepon = models.CharField(max_length=30, default='081234567890')

    class Meta:
        verbose_name = 'Profil Organisasi'
        verbose_name_plural = 'Profil Organisasi'

    def __str__(self):
        return f"{self.nama_organisasi} ({self.periode_kepengurusan})"


class Divisi(models.Model):
    kode = models.CharField(max_length=20, unique=True)
    nama = models.CharField(max_length=100)
    keterangan = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Divisi / Departemen'
        verbose_name_plural = 'Divisi / Departemen'
        ordering = ['nama']

    def __str__(self):
        return f"{self.nama} ({self.kode})"


class Anggota(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profil_anggota')
    nim = models.CharField(max_length=30, unique=True)
    nama = models.CharField(max_length=150)
    divisi = models.ForeignKey(Divisi, on_delete=models.CASCADE, related_name='anggota_list')
    jabatan = models.CharField(max_length=100, default='Staff')
    angkatan = models.PositiveIntegerField(default=2024)
    no_hp = models.CharField(max_length=30, blank=True, default='', help_text="Contoh: 081234567890 atau 6281234567890")
    email = models.EmailField(blank=True, default='')
    status_aktif = models.BooleanField(default=True)
    tanggal_bergabung = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = 'Anggota'
        verbose_name_plural = 'Daftar Anggota'
        ordering = ['divisi', 'nama']

    def __str__(self):
        return f"{self.nim} - {self.nama} ({self.divisi.kode})"

    @property
    def whatsapp_clean(self):
        """Format WhatsApp number to international format without + or spaces."""
        num = ''.join(c for c in str(self.no_hp) if c.isdigit())
        if num.startswith('0'):
            num = '62' + num[1:]
        elif num.startswith('8'):
            num = '62' + num
        return num


class KategoriTransaksi(models.Model):
    JENIS_CHOICES = [
        ('masuk', 'Pemasukan (Kas Masuk)'),
        ('keluar', 'Pengeluaran (Kas Keluar)'),
    ]

    nama = models.CharField(max_length=100)
    jenis = models.CharField(max_length=10, choices=JENIS_CHOICES)
    kode = models.CharField(max_length=20, blank=True, default='')
    deskripsi = models.TextField(blank=True, default='')
    is_iuran_kas = models.BooleanField(default=False, help_text="Tandai jika kategori ini untuk iuran kas rutin anggota")

    class Meta:
        verbose_name = 'Kategori Transaksi'
        verbose_name_plural = 'Kategori Transaksi'
        ordering = ['jenis', 'nama']

    def __str__(self):
        jenis_label = 'Masuk' if self.jenis == 'masuk' else 'Keluar'
        return f"[{jenis_label}] {self.nama}"


class Transaksi(models.Model):
    JENIS_CHOICES = [
        ('masuk', 'Pemasukan'),
        ('keluar', 'Pengeluaran'),
    ]

    kode_transaksi = models.CharField(max_length=50, unique=True)
    tanggal = models.DateField(default=timezone.now)
    jenis = models.CharField(max_length=10, choices=JENIS_CHOICES)
    kategori = models.ForeignKey(KategoriTransaksi, on_delete=models.PROTECT, related_name='transaksi_list')
    nominal = models.DecimalField(max_digits=15, decimal_places=2)
    judul = models.CharField(max_length=200)
    keterangan = models.TextField(blank=True, default='')
    bukti_transaksi = models.FileField(upload_to='bukti_transaksi/', blank=True, null=True)
    divisi_terkait = models.ForeignKey(Divisi, on_delete=models.SET_NULL, null=True, blank=True, related_name='transaksi_terkait')
    dicatat_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Transaksi Kas'
        verbose_name_plural = 'Riwayat Transaksi Kas'
        ordering = ['-tanggal', '-created_at']

    def __str__(self):
        return f"{self.kode_transaksi} | {self.judul} - Rp {self.nominal:,.0f}"

    def save(self, *args, **kwargs):
        if not self.kode_transaksi:
            prefix = "TRX-IN" if self.jenis == 'masuk' else "TRX-OUT"
            today_str = timezone.now().strftime('%Y%m%d')
            count = Transaksi.objects.filter(kode_transaksi__startswith=f"{prefix}-{today_str}").count() + 1
            candidate = f"{prefix}-{today_str}-{count:03d}"
            while Transaksi.objects.filter(kode_transaksi=candidate).exists():
                count += 1
                candidate = f"{prefix}-{today_str}-{count:03d}"
            self.kode_transaksi = candidate
        super().save(*args, **kwargs)


class PeriodeKas(models.Model):
    BULAN_CHOICES = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
    ]

    nama_periode = models.CharField(max_length=50) # e.g. "Januari 2026"
    bulan = models.PositiveSmallIntegerField(choices=BULAN_CHOICES)
    tahun = models.PositiveIntegerField(default=2026)
    nominal = models.DecimalField(max_digits=12, decimal_places=2, default=10000)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Periode Kas'
        verbose_name_plural = 'Daftar Periode Kas'
        ordering = ['tahun', 'bulan']
        unique_together = ('bulan', 'tahun')

    def __str__(self):
        return f"{self.nama_periode} (Rp {self.nominal:,.0f})"


class IuranKas(models.Model):
    STATUS_CHOICES = [
        ('lunas', 'Lunas'),
        ('belum_lunas', 'Belum Lunas'),
    ]
    METODE_CHOICES = [
        ('Transfer', 'Transfer'),
        ('Tunai', 'Tunai'),
    ]

    anggota = models.ForeignKey(Anggota, on_delete=models.CASCADE, related_name='iuran_list')
    periode = models.ForeignKey(PeriodeKas, on_delete=models.CASCADE, related_name='iuran_periode_list')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='belum_lunas')
    nominal_dibayar = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tanggal_bayar = models.DateField(null=True, blank=True)
    metode_pembayaran = models.CharField(max_length=30, choices=METODE_CHOICES, default='Transfer')
    catatan = models.CharField(max_length=200, blank=True, default='')
    transaksi = models.ForeignKey(Transaksi, on_delete=models.SET_NULL, null=True, blank=True, related_name='iuran_terkait')

    class Meta:
        verbose_name = 'Iuran Kas Anggota'
        verbose_name_plural = 'Data Iuran Kas Anggota'
        unique_together = ('anggota', 'periode')
        ordering = ['periode', 'anggota']

    def __str__(self):
        return f"{self.anggota.nama} - {self.periode.nama_periode} ({self.status.upper()})"


class PengajuanIuran(models.Model):
    STATUS_CHOICES = [
        ('menunggu', 'Menunggu Verifikasi'),
        ('disetujui', 'Disetujui'),
        ('ditolak', 'Ditolak'),
    ]
    METODE_CHOICES = [
        ('Transfer', 'Transfer'),
        ('Tunai', 'Tunai'),
    ]

    anggota = models.ForeignKey(Anggota, on_delete=models.CASCADE, related_name='pengajuan_list')
    periode = models.ForeignKey(PeriodeKas, on_delete=models.CASCADE, related_name='pengajuan_list')
    nominal = models.DecimalField(max_digits=12, decimal_places=2)
    metode_pembayaran = models.CharField(max_length=30, choices=METODE_CHOICES, default='Transfer')
    bukti_transfer = models.FileField(upload_to='bukti_transfer_anggota/')
    catatan = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')
    catatan_bendahara = models.CharField(max_length=255, blank=True, default='')
    tanggal_pengajuan = models.DateTimeField(auto_now_add=True)
    diverifikasi_pada = models.DateTimeField(null=True, blank=True)
    diverifikasi_oleh = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Pengajuan Pembayaran Iuran'
        verbose_name_plural = 'Pengajuan Pembayaran Iuran'
        ordering = ['-tanggal_pengajuan']

    def __str__(self):
        return f"Pengajuan Kas {self.anggota.nama} - {self.periode.nama_periode} ({self.get_status_display()})"
