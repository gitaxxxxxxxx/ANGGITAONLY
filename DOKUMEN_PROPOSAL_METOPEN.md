# DOKUMEN PROPOSAL & SPESIFIKASI SISTEM (METOPEN)

**Judul Penelitian:**  
**Rancang Bangun Sistem Informasi Manajemen Kas Organisasi Kemahasiswaan Berbasis Web dengan Fitur Rekapitulasi Otomatis**

---

## BAB I: PENDAHULUAN

### 1.1 Latar Belakang Masalah
Organisasi kemahasiswaan (Ormawa) seperti Badan Eksekutif Mahasiswa (BEM), Himpunan Mahasiswa Jurusan (HIMA), dan Unit Kegiatan Mahasiswa (UKM) memiliki intensitas kegiatan yang tinggi. Setiap kegiatan memerlukan pengelolaan dana operasional dan kas yang tertib, transparan, dan akuntabel.

Namun pada praktiknya, pengelolaan kas organisasi mahasiswa masih menghadapi berbagai kendala mendasar:
1. **Pencatatan Konvensional & Terfragmentasi**: Mayoritas bendahara ormawa masih mencatat arus kas masuk dan kas keluar menggunakan buku kas fisik, spreadsheet terpisah, atau obrolan grup WhatsApp yang rawan tercecer dan hilang.
2. **Kesulitan Melacak Iuran Rutin Anggota**: Penagihan iuran kas wajib anggota bulanan seringkali tidak terdata rapi. Bendahara kesulitan mengetahui anggota mana saja yang menunggak berapa bulan, sehingga penagihan kas menjadi tidak efektif dan target kas tidak tercapai.
3. **Penyusunan Laporan Pertanggungjawaban (LPJ) Keuangan yang Memakan Waktu**: Saat akhir periode atau menjelang pergantian pengurus, bendahara harus merekapitulasi ratusan transaksi secara manual untuk membuat buku kas LPJ. Proses rekap manual ini rawan kesalahan hitung (*human error*), perbedaan saldo, dan memakan waktu berhari-hari.
4. **Kurangnya Transparansi Finansial**: Anggota organisasi dan pimpinan kesulitan memantau kondisi saldo riil kas organisasi secara *real-time*.

Berdasarkan permasalahan tersebut, dibutuhkan sebuah **Sistem Informasi Manajemen Kas Organisasi Kemahasiswaan Berbasis Web dengan Fitur Rekapitulasi Otomatis** yang mampu mengagregasi data keuangan secara langsung, memvisualisasikan matriks iuran kas anggota, serta mengenerasi dokumen LPJ siap cetak.

### 1.2 Rumusan Masalah
1. Bagaimana merancang dan membangun sistem informasi kas organisasi kemahasiswaan berbasis web yang mudah digunakan oleh bendahara?
2. Bagaimana mengimplementasikan fitur rekapitulasi otomatis untuk mengagregasi arus kas bulanan, surplus/defisit, dan alokasi anggaran tanpa perhitungan manual?
3. Bagaimana menyajikan matriks kepatuhan iuran kas rutin anggota yang terintegrasi dengan pengingat tagihan WhatsApp otomatis?
4. Bagaimana menghasilkan Laporan Pertanggungjawaban (LPJ) keuangan formal berstandar kampus lengkap dengan kop surat dan kolom pengesahan tiga pihak?

### 1.3 Tujuan Penelitian
1. Mengembangkan sistem informasi manajemen kas berbasis web yang mengotomatisasi pembukuan kas masuk dan kas keluar organisasi kemahasiswaan.
2. Menerapkan modul rekapitulasi otomatis yang menghitung akumulasi saldo awal, mutasi kas, surplus/defisit, dan saldo akhir secara instan.
3. Membangun matriks visual status pembayaran iuran kas anggota 12 bulan dengan fitur penagihan pesan WhatsApp otomatis (*1-click WhatsApp reminder*).
4. Menyediakan fitur cetak LPJ Keuangan resmi berstandar A4 yang siap ditandatangani oleh Bendahara Umum, Ketua Umum, dan Dosen Pembina Kemahasiswaan.

---

## BAB II: KAJIAN PUSTAKA & LANDASAN TEORI

### 2.1 Konsep Sistem Informasi Keuangan Organisasi
Sistem informasi manajemen kas adalah sistem berbasis komputer yang menyediakan informasi historis dan terkini mengenai penerimaan dan pengeluaran kas guna mendukung akuntabilitas dan pengambilan keputusan manajerial organisasi.

### 2.2 Fitur Rekapitulasi Otomatis
Rekapitulasi otomatis dalam penelitian ini didefinisikan sebagai mekanisme agregasi data berbasis kueri basis data relasional yang mengelompokkan transaksi kas berdasarkan dimensi waktu (harian, bulanan, tahunan), dimensi kategori belanja, dan dimensi departemen/divisi. Fitur ini secara berkelanjutan memperbarui nilai saldo awal berjalan (*running beginning balance*) dan saldo penutupan (*closing balance*) tanpa intervensi manual bendahara.

### 2.3 Teknologi yang Digunakan
1. **Python & Django Framework**: Dipilih karena arsitektur MVT (*Model-View-Template*) yang kokoh, keamanan bawaan terhadap serangan CSRF dan SQL Injection, serta ORM (*Object-Relational Mapping*) yang sangat tangguh untuk kalkulasi agregasi keuangan.
2. **SQLite3**: Basis data relasional berkinerja tinggi, zero-configuration, dan self-contained yang sangat ideal untuk organisasi kemahasiswaan.
3. **Tailwind CSS 3**: Framework utilitas CSS modern untuk mewujudkan antarmuka responsif dan estetik.
4. **Chart.js**: Pustaka JavaScript untuk visualisasi grafik tren arus kas bulanan dan diagram alokasi anggaran.

---

## BAB III: METODOLOGI PENELITIAN & PERANCANGAN

### 3.1 Metode Pengembangan Sistem (SDLC Waterfall)
Penelitian ini menggunakan metode pengembangan perangkat lunak model Waterfall (Air Terjun) dengan tahapan:
1. **Analisis Kebutuhan (Requirements Analysis)**: Mengidentifikasi kebutuhan fungsional dan non-fungsional bendahara ormawa.
2. **Perancangan Sistem (System Design)**: Perancangan skema basis data relasional (ERD), Data Flow Diagram (DFD) / Use Case Diagram, dan perancangan antarmuka (UI/UX).
3. **Implementasi (Implementation / Coding)**: Pengkodean backend menggunakan Django dan frontend menggunakan Tailwind CSS serta Chart.js.
4. **Pengujian (Testing)**: Pengujian fungsionalitas menggunakan metode *Black-Box Testing*.

### 3.2 Analisis Kebutuhan Fungsional (Functional Requirements)
- **F-01**: Sistem dapat mencatat transaksi kas masuk dan kas keluar lengkap dengan upload bukti fisik nota.
- **F-02**: Sistem dapat menyajikan dashboard arus kas eksekutif dengan grafik tren 12 bulan dan ringkasan saldo.
- **F-03**: Sistem dapat mengelola data anggota organisasi mahasiswa dan divisinya.
- **F-04**: Sistem dapat menampilkan matriks iuran kas 12 bulan dan memverifikasi status bayar dengan 1 kali klik.
- **F-05**: Sistem dapat menghasilkan tautan pengingat tagihan ke nomor WhatsApp anggota yang menunggak kas.
- **F-06**: Sistem dapat merekapitulasi arus kas bulanan secara otomatis (saldo awal, mutasi masuk, mutasi keluar, surplus/defisit, saldo akhir).
- **F-07**: Sistem dapat mengenerasi format Laporan Pertanggungjawaban (LPJ) resmi siap cetak format A4 lengkap dengan kop surat dan kolom tanda tangan pengesahan.
- **F-08**: Sistem dapat mengekspor data laporan ke format spreadsheet CSV/Excel.

### 3.3 Struktur Entitas Basis Data (Entity Relationship)
1. **ProfilOrganisasi**: Menyimpan data identitas ormawa, nama pimpinan, pembina, nominal iuran, dan saldo awal.
2. **Divisi**: Menyimpan data departemen dalam ormawa (BPH, PSDM, KOMINFO, KASTRAT, DANUS, SOSMA).
3. **Anggota**: Menyimpan identitas mahasiswa (NIM, Nama, Divisi, Jabatan, Angkatan, No HP).
4. **PeriodeKas**: Menyimpan periode bulan dan tahun penarikan kas rutin wajib.
5. **IuranKas**: Relasi *many-to-many* antara Anggota dan PeriodeKas yang mencatat status lunas/tunggakan dan metode bayar.
6. **KategoriTransaksi**: Pos-pos penerimaan dan pengeluaran kas ormawa.
7. **Transaksi**: Buku besar pencatatan kas riil (tanggal, jenis, nominal, kategori, divisi terkait, bukti nota, dicatat oleh).
