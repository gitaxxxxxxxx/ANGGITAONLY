from django.contrib import admin
from .models import (
    ProfilOrganisasi, Divisi, Anggota,
    KategoriTransaksi, Transaksi, PeriodeKas, IuranKas, PengajuanIuran
)

@admin.register(ProfilOrganisasi)
class ProfilOrganisasiAdmin(admin.ModelAdmin):
    list_display = ('nama_organisasi', 'singkatan', 'periode_kepengurusan', 'nominal_kas_wajib', 'saldo_awal')

@admin.register(Divisi)
class DivisiAdmin(admin.ModelAdmin):
    list_display = ('kode', 'nama', 'keterangan')
    search_fields = ('kode', 'nama')

@admin.register(Anggota)
class AnggotaAdmin(admin.ModelAdmin):
    list_display = ('nim', 'nama', 'divisi', 'jabatan', 'angkatan', 'no_hp', 'status_aktif')
    list_filter = ('divisi', 'angkatan', 'status_aktif')
    search_fields = ('nim', 'nama', 'no_hp')

@admin.register(KategoriTransaksi)
class KategoriTransaksiAdmin(admin.ModelAdmin):
    list_display = ('nama', 'jenis', 'kode', 'is_iuran_kas')
    list_filter = ('jenis', 'is_iuran_kas')

@admin.register(Transaksi)
class TransaksiAdmin(admin.ModelAdmin):
    list_display = ('kode_transaksi', 'tanggal', 'jenis', 'kategori', 'nominal', 'judul', 'divisi_terkait')
    list_filter = ('jenis', 'kategori', 'divisi_terkait', 'tanggal')
    search_fields = ('kode_transaksi', 'judul', 'keterangan')

@admin.register(PeriodeKas)
class PeriodeKasAdmin(admin.ModelAdmin):
    list_display = ('nama_periode', 'bulan', 'tahun', 'nominal', 'is_active')
    list_filter = ('tahun', 'is_active')

@admin.register(IuranKas)
class IuranKasAdmin(admin.ModelAdmin):
    list_display = ('anggota', 'periode', 'status', 'nominal_dibayar', 'tanggal_bayar', 'metode_pembayaran')
    list_filter = ('status', 'periode__tahun', 'periode__bulan', 'metode_pembayaran')
    search_fields = ('anggota__nama', 'anggota__nim')

@admin.register(PengajuanIuran)
class PengajuanIuranAdmin(admin.ModelAdmin):
    list_display = ('anggota', 'periode', 'nominal', 'metode_pembayaran', 'status', 'tanggal_pengajuan')
    list_filter = ('status', 'metode_pembayaran', 'tanggal_pengajuan')
    search_fields = ('anggota__nama', 'anggota__nim')
