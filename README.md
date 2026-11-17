# Rancang Bangun Sistem Informasi Manajemen Kas Organisasi Kemahasiswaan Berbasis Web dengan Fitur Rekapitulasi Otomatis (SIMKAS-ORMAWA)

Aplikasi web modern yang dikembangkan khusus untuk mempermudah bendahara dan pengurus organisasi mahasiswa (BEM, Himpunan Mahasiswa, UKM) dalam mengelola pembukuan kas masuk, kas keluar, iuran rutin bulanan anggota, serta menghasilkan **Laporan Pertanggungjawaban (LPJ) Keuangan** secara otomatis, transparan, dan akurat.

---

## 🌟 Fitur Utama Sistem

### 1. 📊 Dashboard Eksekutif Arus Kas Real-Time
- **Total Saldo Kas Berjalan**, Total Kas Masuk, Total Kas Keluar, dan Saldo Awal Kepengurusan.
- **Grafik Tren Arus Kas Bulanan (Line Chart)**: Membandingkan arus masuk dan keluar selama 12 bulan berjalan menggunakan Chart.js.
- **Grafik Distribusi Kategori (Doughnut Chart)**: Visualisasi komposisi pos belanja pengeluaran dan pos pemasukan dana.
- **Tabel 10 Transaksi Terakhir** dilengkapi status tipe kas, divisi terkait, dan tombol pratinjau bukti nota.

### 2. ⚡ Fitur Unggulan: Rekapitulasi Arus Kas Otomatis
- **Rekapitulasi Bulanan Dinamis**: Sistem secara otomatis mengagregasi saldo awal berjalan, mutasi masuk, mutasi keluar, surplus/defisit bersih, dan saldo akhir setiap bulan (Januari - Desember) tanpa perlu kalkulasi manual.
- **Rekapitulasi per Kategori & Divisi**: Melacak serapan anggaran program kerja setiap divisi dan kontribusi penerimaan kas.
- **Evaluasi Kepatuhan Kas**: Mengidentifikasi persentase kepatuhan kas anggota serta daftar mahasiswa dengan tunggakan terbanyak untuk tindak lanjut cepat.

### 3. 📅 Matriks Iuran Kas Rutin Anggota (12 Bulan)
- **Tabel Matriks Interaktif**: Visualisasi grid status pembayaran iuran wajib setiap anggota per bulan (Jan - Des).
- **Toggle Status 1-Klik**: Verifikasi lunas atau belum lunas secara langsung (otomatis mencatat transaksi penerimaan kas).
- **Pengingat Tagihan WhatsApp Otomatis**: Tombol *Tagih WA* yang langsung membuka WhatsApp Web/App (`wa.me`) dengan pesan pengingat tagihan personal dan santun.
- **Setor Kas Cepat**: Form multi-bulan untuk mencatat pembayaran kas beberapa bulan sekaligus dengan pilihan metode Tunai, Transfer Bank, atau QRIS.

### 4. 🖨️ Generator Laporan Pertanggungjawaban (LPJ) Siap Cetak (A4 Resmi)
- Format standar dokumen resmi kemahasiswaan:
  - **Kop Surat Resmi Ormawa** lengkap dengan logo, nama universitas, fakultas, nomor surat, dan garis ganda kop surat.
  - **Ikhtisar Posisi Saldo Kas** (Saldo Awal, Pemasukan, Pengeluaran, Saldo Tutup Buku).
  - **Tabel Rincian Penerimaan Kas** (Nomor, Tanggal, Kategori, Uraian, Nominal).
  - **Tabel Rincian Pengeluaran Kas** (Nomor, Tanggal, Kategori/Divisi, Uraian Belanja, Nominal).
  - **Lembar Pengesahan Tiga Pihak**: Kolom tanda tangan resmi Bendahara Umum, Ketua Umum, dan Dosen Pembina Kemahasiswaan.
  - Cetak langsung ke printer atau Simpan sebagai PDF (`window.print()`).

### 5. 💰 Pencatatan Transaksi Kas Masuk & Kas Keluar
- Form pencatatan lengkap: Tipe (Masuk/Keluar), Kategori Transaksi, Nominal Rupiah, Tanggal, Divisi Terkait, Keterangan, dan **Upload Bukti Transaksi/Nota/Struk**.
- Filter lanjutan: Rentang tanggal (dari/sampai), jenis transaksi, kategori, dan pencarian judul/kode transaksi.
- Ringkasan akumulasi hasil filter dan **Ekspor Laporan Transaksi ke CSV/Excel**.

### 6. 👥 Manajemen Data Anggota & Divisi
- Pencatatan identitas anggota ormawa: NIM, Nama Lengkap, Divisi/Departemen, Jabatan, Angkatan, No WhatsApp, dan Status Keaktifan.
- Kartu Detail Anggota: Melacak histori pembayaran kas bulanan setiap anggota secara spesifik.

### 7. ⚙️ Pengaturan Profil Ormawa & Master Kategori
- Kustomisasi identitas organisasi, nama kampus, nama pimpinan & pembina ormawa untuk kop surat.
- Pengaturan nominal kas wajib bulanan dan saldo awal kepengurusan.
- Pengelolaan kategori pemasukan dan pengeluaran dinamis.

---

## 🛠️ Arsitektur & Teknologi

| Komponen | Teknologi |
| :--- | :--- |
| **Backend Framework** | Python 3.15 + Django 6.1.3 |
| **Database** | SQLite3 (Zero-Configuration, Self-Contained) |
| **Frontend Styling** | Tailwind CSS 3 (Modern, Responsive, Emerald Theme) |
| **Visualisasi Grafik** | Chart.js |
| **Icon Pack** | Lucide Icons |
| **Format Cetak** | HTML5 Print Media CSS (Standar A4 Formal Akademik) |

---

## 🚀 Cara Menjalankan Aplikasi

### Cara 1: Menggunakan File Batch (Paling Praktis di Windows)
Cukup klik dua kali file **`jalankan_sistem.bat`** yang ada di folder ini. Server akan langsung aktif dan membuka aplikasi di browser Anda.

### Cara 2: Menjalankan Melalui Terminal / PowerShell
1. Buka PowerShell atau Command Prompt pada folder ini:
   ```powershell
   cd "c:\Users\ASUS\Documents\KULIAH\Metopen"
   ```
2. Jalankan perintah server Django:
   ```powershell
   python manage.py runserver 127.0.0.1:8000
   ```
3. Buka browser Anda dan akses:
   ```
   http://127.0.0.1:8000/
   ```

---

## 🔑 Akun Login Default

| Role | Username | Password | Keterangan |
| :--- | :--- | :--- | :--- |
| **Administrator / Bendahara Umum** | `admin` | `admin123` | Hak akses penuh mengelola kas, iuran, transaksi, dan pengaturan |
| **Akses Tamu / Penguji** | *Langsung Jelajah* | - | Tersedia tombol jelajah langsung dari halaman login |

---

## 📁 Struktur Direktori Proyek

```
Metopen/
├── config/                 # Konfigurasi Inti Django (Settings, URLs, WSGI)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── kas_app/                # Aplikasi Kas Organisasi Kemahasiswaan
│   ├── migrations/         # Skema Migrasi Database
│   ├── templatetags/       # Custom Filter Mata Uang Rupiah & Helper
│   │   ├── __init__.py
│   │   └── kas_tags.py
│   ├── admin.py            # Registrasi Django Admin Panel
│   ├── context_processors.py # Injeksi Profil Organisasi ke Seluruh Template
│   ├── models.py           # Model Database (Profil, Divisi, Anggota, Transaksi, Iuran, Periode)
│   ├── urls.py             # Routing URL SIMKAS ORMAWA
│   └── views.py            # Logika Bisnis & Fitur Rekapitulasi Otomatis
├── templates/              # Antarmuka Pengguna (UI)
│   ├── base.html           # Layout Induk (Sidebar, Navbar, Modal Cepat)
│   └── kas_app/
│       ├── dashboard.html      # Dashboard Utama & Grafik Arus Kas
│       ├── transaksi_list.html # Daftar & Filter Transaksi
│       ├── transaksi_form.html # Form Input/Edit Transaksi & Upload Nota
│       ├── iuran_matrix.html   # Matriks Pembayaran Iuran Kas 12 Bulan
│       ├── rekapitulasi.html   # Fitur Rekapitulasi Arus Kas Otomatis
│       ├── cetak_lpj.html      # LPJ Resmi Siap Cetak (A4 + Kop Surat)
│       ├── anggota_list.html   # Daftar Anggota Ormawa
│       ├── anggota_form.html   # Form Tambah/Edit Anggota
│       ├── anggota_detail.html # Kartu Histori Kas Per Anggota
│       ├── pengaturan.html     # Pengaturan Profil Ormawa & Kategori
│       ├── confirm_delete.html # Konfirmasi Hapus Data
│       └── login.html          # Halaman Login Elegan
├── media/                  # Penyimpanan Bukti Nota/Struk & Logo
├── static/                 # Aset Statis
├── db.sqlite3              # Database SQLite (Sudah terisi data simulasi ormawa)
├── seed_data.py            # Script Generator Data Sampel Realistis
├── jalankan_sistem.bat     # Shortcut Sekali Klik untuk Menjalankan Web
├── manage.py
└── README.md
```

---

## 🎓 Relevansi dengan Mata Kuliah Metode Penelitian (Metopen)

Aplikasi ini dapat langsung dijadikan sebagai objek studi dan artefak implementasi dalam proposal penelitian Metopen dengan judul:
**"Rancang Bangun Sistem Informasi Manajemen Kas Organisasi Kemahasiswaan Berbasis Web dengan Fitur Rekapitulasi Otomatis"**.

- **Metode Pengembangan**: Rekayasa Perangkat Lunak menggunakan metode **SDLC Waterfall** atau **Agile / Prototyping**.
- **Analisis Kebutuhan**:
  - Kebutuhan Fungsional: Pencatatan kas masuk/keluar, matriks iuran rutin anggota, generator laporan LPJ otomatis, dan notifikasi pengingat via WhatsApp.
  - Kebutuhan Non-Fungsional: Antarmuka responsif (Tailwind CSS), visualisasi data interaktif (Chart.js), dan integritas data akuntansi.
- **Metode Pengujian**:
  - *Black-Box Testing* untuk menguji seluruh fungsi transaksi dan rekapitulasi otomatis.
  - *User Acceptance Testing (UAT)* kepada bendahara organisasi mahasiswa.
