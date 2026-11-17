from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),

    # Autentikasi
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Transaksi Kas
    path('transaksi/', views.transaksi_list_view, name='transaksi_list'),
    path('transaksi/tambah/', views.transaksi_create_view, name='transaksi_create'),
    path('transaksi/<int:pk>/edit/', views.transaksi_update_view, name='transaksi_update'),
    path('transaksi/<int:pk>/hapus/', views.transaksi_delete_view, name='transaksi_delete'),
    path('transaksi/export/csv/', views.transaksi_export_csv, name='transaksi_export_csv'),

    # Iuran Kas Anggota & Matriks
    path('iuran/', views.iuran_matrix_view, name='iuran_matrix'),
    path('iuran/bayar-cepat/', views.iuran_bayar_cepat, name='iuran_bayar_cepat'),
    path('iuran/toggle-status/<int:iuran_id>/', views.iuran_toggle_status, name='iuran_toggle_status'),
    path('iuran/generate-periode/<int:tahun>/', views.generate_periode_tahunan, name='generate_periode_tahunan'),

    # Rekapitulasi Otomatis & LPJ
    path('rekapitulasi/', views.rekapitulasi_view, name='rekapitulasi'),
    path('rekapitulasi/lpj/', views.cetak_lpj_view, name='cetak_lpj'),
    path('rekapitulasi/export/bulanan-csv/', views.rekap_bulanan_export_csv, name='rekap_bulanan_export_csv'),

    # Anggota
    path('anggota/', views.anggota_list_view, name='anggota_list'),
    path('anggota/tambah/', views.anggota_create_view, name='anggota_create'),
    path('anggota/<int:pk>/edit/', views.anggota_update_view, name='anggota_update'),
    path('anggota/<int:pk>/hapus/', views.anggota_delete_view, name='anggota_delete'),
    path('anggota/<int:pk>/', views.anggota_detail_view, name='anggota_detail'),

    # Pengaturan Profil & Kategori
    path('pengaturan/', views.pengaturan_view, name='pengaturan'),
    path('pengaturan/kategori/tambah/', views.kategori_create_view, name='kategori_create'),
    path('pengaturan/kategori/<int:pk>/hapus/', views.kategori_delete_view, name='kategori_delete'),
]
