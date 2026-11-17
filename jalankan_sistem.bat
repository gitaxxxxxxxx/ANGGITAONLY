@echo off
title SIMKAS ORMAWA - Sistem Informasi Manajemen Kas Organisasi Kemahasiswaan
color 0A
cls
echo =======================================================================
echo     SIMKAS ORMAWA - SISTEM INFORMASI MANAJEMEN KAS KEMAHASISWAAN
echo     Fitur: Rekapitulasi Kas Otomatis, Matriks Iuran & LPJ Siap Cetak
echo =======================================================================
echo.
echo Sedang menyiapkan server lokal...
echo Membuka di browser: http://127.0.0.1:8000/
echo.
echo Akun Login Default:
echo   - Username : admin
echo   - Password : admin123
echo.
echo Tekan CTRL + C di jendela ini jika ingin menghentikan server.
echo =======================================================================
echo.

python manage.py runserver 127.0.0.1:8000
pause
