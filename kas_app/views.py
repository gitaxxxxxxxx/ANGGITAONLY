import csv
import os
from datetime import datetime, date
from decimal import Decimal
import urllib.parse

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.paginator import Paginator

from .models import (
    ProfilOrganisasi, Divisi, Anggota,
    KategoriTransaksi, Transaksi, PeriodeKas, IuranKas, PengajuanIuran
)


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def generate_mock_transfer_receipt(anggota, periode, metode='Transfer Bank', catatan=''):
    """Membuat resi transfer visual otomatis jika tidak ada file fisik yang diunggah."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        media_sub = 'bukti_transfer_anggota'
        dest_dir = os.path.join(settings.MEDIA_ROOT, media_sub)
        os.makedirs(dest_dir, exist_ok=True)
        fname = f"receipt_{anggota.nim}_{periode.id}_{int(timezone.now().timestamp())}.png"
        fpath = os.path.join(dest_dir, fname)

        w, h = 600, 850
        img = Image.new('RGB', (w, h), color='#F8FAFC')
        draw = ImageDraw.Draw(img)

        header_color = '#00529C' if 'BCA' in metode else ('#16A34A' if 'QRIS' in metode else '#1E3A8A')
        draw.rectangle([0, 0, w, 110], fill=header_color)
        draw.rounded_rectangle([25, 80, w-25, h-40], radius=20, fill='#FFFFFF', outline='#E2E8F0', width=2)

        # Checkmark icon
        draw.ellipse([w//2 - 35, 120, w//2 + 35, 190], fill='#DCFCE7', outline='#22C55E', width=3)
        draw.line([w//2 - 15, 155, w//2 - 3, 168], fill='#16A34A', width=4)
        draw.line([w//2 - 3, 168, w//2 + 18, 142], fill='#16A34A', width=4)

        try:
            font_xl = ImageFont.truetype('arialbd.ttf', 30)
            font_md = ImageFont.truetype('arialbd.ttf', 17)
            font_sm = ImageFont.truetype('arial.ttf', 15)
            font_xs = ImageFont.truetype('arial.ttf', 13)
            font_head = ImageFont.truetype('arialbd.ttf', 24)
        except:
            font_xl = font_md = font_sm = font_xs = font_head = ImageFont.load_default()

        draw.text((35, 40), f'{metode.upper()}', fill='#FFFFFF', font=font_head)
        draw.text((w-180, 45), 'RESI RESMI', fill='#E0F2FE', font=font_sm)

        draw.text((w//2, 215), 'TRANSFER BERHASIL', fill='#0F172A', font=font_xl, anchor='mm')
        now_str = timezone.now().strftime('%d %b %Y %H:%M WIB')
        draw.text((w//2, 250), now_str, fill='#64748B', font=font_sm, anchor='mm')

        draw.rounded_rectangle([60, 280, w-60, 360], radius=15, fill='#F0FDF4', outline='#BBF7D0', width=1)
        draw.text((w//2, 305), 'Total Pembayaran', fill='#166534', font=font_xs, anchor='mm')
        draw.text((w//2, 335), f'Rp {periode.nominal:,.0f}'.replace(',', '.'), fill='#15803D', font=font_xl, anchor='mm')

        draw.line([50, 385, w-50, 385], fill='#E2E8F0', width=1)

        details = [
            ('No. Referensi', f'TRF{int(timezone.now().timestamp())}'),
            ('Nama Pengirim', anggota.nama),
            ('NIM Mahasiswa', anggota.nim),
            ('Penerima', 'BEM FASILKOM UI (KAS UTAMA)'),
            ('Bank Tujuan', 'BCA (014) - Rek. 8820192831'),
            ('Peruntukan', f'Iuran Kas {periode.nama_periode}'),
            ('Catatan', catatan or 'Tanpa catatan tambahan'),
            ('Status', 'BERHASIL / SUKSES'),
        ]

        y = 410
        for k, v in details:
            draw.text((60, y), k, fill='#64748B', font=font_sm)
            draw.text((w-60, y), str(v)[:32], fill='#0F172A' if k != 'Status' else '#16A34A', font=font_md if k in ['Nama Pengirim', 'Status'] else font_sm, anchor='ra')
            y += 45
            if y < 730:
                draw.line([60, y-10, w-60, y-10], fill='#F1F5F9', width=1)

        draw.text((w//2, h-65), 'Simpan resi transfer ini sebagai bukti pembayaran kas sah.', fill='#94A3B8', font=font_xs, anchor='mm')
        img.save(fpath, 'PNG')
        return f"{media_sub}/{fname}"
    except Exception as e:
        return ""
def get_profil():
    profil = ProfilOrganisasi.objects.first()
    if not profil:
        profil = ProfilOrganisasi.objects.create(
            nama_organisasi='BEM Fakultas Ilmu Komputer',
            nama_institusi='Universitas Indonesia',
            singkatan='BEM FASILKOM',
            periode_kepengurusan='2026/2027',
            nama_ketua='Muhammad Fikri Pratama',
            nim_ketua='2308101001',
            nama_bendahara='Nabila Nur Azizah',
            nim_bendahara='2308101015',
            nama_pembina='Dr. Eng. Ir. Bambang Hermanto, M.T.',
            nip_pembina='198205142006041002',
            nominal_kas_wajib=Decimal('10000'),
            periode_kas='bulanan',
            saldo_awal=Decimal('500000')
        )
    return profil


def pastikan_periode_tahun(tahun):
    """Memastikan 12 bulan periode kas untuk tahun tertentu sudah dibuat."""
    profil = get_profil()
    bulan_list = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
    ]
    for b_num, b_nama in bulan_list:
        PeriodeKas.objects.get_or_create(
            bulan=b_num,
            tahun=tahun,
            defaults={
                'nama_periode': f"{b_nama} {tahun}",
                'nominal': profil.nominal_kas_wajib,
                'is_active': True
            }
        )


def sinkronisasi_iuran_anggota(tahun):
    """Memastikan seluruh anggota aktif memiliki record iuran pada tahun terkait."""
    pastikan_periode_tahun(tahun)
    anggota_list = Anggota.objects.filter(status_aktif=True)
    periode_list = PeriodeKas.objects.filter(tahun=tahun)

    for anggota in anggota_list:
        for periode in periode_list:
            IuranKas.objects.get_or_create(
                anggota=anggota,
                periode=periode,
                defaults={
                    'status': 'belum_lunas',
                    'nominal_dibayar': Decimal('0'),
                }
            )


# ==========================================
# DASHBOARD
# ==========================================
def dashboard_view(request):
    # Jika yang login adalah Anggota (Bukan Staff/Bendahara), arahkan ke Portal Khusus Anggota
    if request.user.is_authenticated and hasattr(request.user, 'profil_anggota') and not request.user.is_staff:
        return redirect('portal_anggota')

    profil = get_profil()
    current_year = timezone.now().year

    # Pastikan data periode tahun ini ada
    pastikan_periode_tahun(current_year)
    sinkronisasi_iuran_anggota(current_year)

    # Agregasi Kas Keseluruhan
    total_masuk = Transaksi.objects.filter(jenis='masuk').aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')
    total_keluar = Transaksi.objects.filter(jenis='keluar').aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')
    saldo_akhir = profil.saldo_awal + total_masuk - total_keluar

    # Transaksi Bulan Ini
    now = timezone.now()
    masuk_bulan_ini = Transaksi.objects.filter(
        jenis='masuk',
        tanggal__year=now.year,
        tanggal__month=now.month
    ).aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')

    keluar_bulan_ini = Transaksi.objects.filter(
        jenis='keluar',
        tanggal__year=now.year,
        tanggal__month=now.month
    ).aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')

    # Statistik Iuran Kas
    total_anggota_aktif = Anggota.objects.filter(status_aktif=True).count()
    iuran_tahun_ini = IuranKas.objects.filter(periode__tahun=current_year)
    total_tagihan_iuran = sum(i.periode.nominal for i in iuran_tahun_ini)
    total_iuran_terkumpul = iuran_tahun_ini.filter(status='lunas').aggregate(Sum('nominal_dibayar'))['nominal_dibayar__sum'] or Decimal('0')
    total_tunggakan = total_tagihan_iuran - total_iuran_terkumpul
    persen_kepatuhan = 0
    if total_tagihan_iuran > 0:
        persen_kepatuhan = round((total_iuran_terkumpul / total_tagihan_iuran) * 100, 1)

    # 10 Transaksi Terakhir
    transaksi_terbaru = Transaksi.objects.select_related('kategori', 'divisi_terkait').all()[:10]

    # Data Grafik Tren Kas Bulanan (12 Bulan Tahun Berjalan)
    bulan_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
    data_masuk_bulanan = []
    data_keluar_bulanan = []
    for b in range(1, 13):
        m = Transaksi.objects.filter(
            jenis='masuk',
            tanggal__year=current_year,
            tanggal__month=b
        ).aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')
        k = Transaksi.objects.filter(
            jenis='keluar',
            tanggal__year=current_year,
            tanggal__month=b
        ).aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')
        data_masuk_bulanan.append(float(m))
        data_keluar_bulanan.append(float(k))

    # Data Grafik Kategori Pemasukan & Pengeluaran
    kategori_masuk = Transaksi.objects.filter(jenis='masuk').values('kategori__nama').annotate(total=Sum('nominal')).order_by('-total')[:5]
    kategori_keluar = Transaksi.objects.filter(jenis='keluar').values('kategori__nama').annotate(total=Sum('nominal')).order_by('-total')[:5]

    labels_kat_masuk = [item['kategori__nama'] for item in kategori_masuk]
    values_kat_masuk = [float(item['total']) for item in kategori_masuk]

    labels_kat_keluar = [item['kategori__nama'] for item in kategori_keluar]
    values_kat_keluar = [float(item['total']) for item in kategori_keluar]

    # Daftar Kategori untuk Modal Input Cepat
    kategori_all = KategoriTransaksi.objects.all()
    divisi_all = Divisi.objects.all()

    context = {
        'profil': profil,
        'saldo_akhir': saldo_akhir,
        'total_masuk': total_masuk,
        'total_keluar': total_keluar,
        'masuk_bulan_ini': masuk_bulan_ini,
        'keluar_bulan_ini': keluar_bulan_ini,
        'total_anggota_aktif': total_anggota_aktif,
        'total_iuran_terkumpul': total_iuran_terkumpul,
        'total_tunggakan': total_tunggakan,
        'persen_kepatuhan': persen_kepatuhan,
        'transaksi_terbaru': transaksi_terbaru,
        'bulan_labels': bulan_labels,
        'data_masuk_bulanan': data_masuk_bulanan,
        'data_keluar_bulanan': data_keluar_bulanan,
        'labels_kat_masuk': labels_kat_masuk,
        'values_kat_masuk': values_kat_masuk,
        'labels_kat_keluar': labels_kat_keluar,
        'values_kat_keluar': values_kat_keluar,
        'kategori_all': kategori_all,
        'divisi_all': divisi_all,
        'current_year': current_year,
    }
    return render(request, 'kas_app/dashboard.html', context)


# ==========================================
# TRANSAKSI KAS
# ==========================================
def transaksi_list_view(request):
    transaksi_qs = Transaksi.objects.select_related('kategori', 'divisi_terkait', 'dicatat_oleh').all()

    # Filter
    search = request.GET.get('search', '').strip()
    jenis = request.GET.get('jenis', '').strip()
    kategori_id = request.GET.get('kategori', '').strip()
    tanggal_mulai = request.GET.get('tanggal_mulai', '').strip()
    tanggal_selesai = request.GET.get('tanggal_selesai', '').strip()

    if search:
        transaksi_qs = transaksi_qs.filter(
            Q(judul__icontains=search) |
            Q(keterangan__icontains=search) |
            Q(kode_transaksi__icontains=search)
        )
    if jenis in ['masuk', 'keluar']:
        transaksi_qs = transaksi_qs.filter(jenis=jenis)
    if kategori_id:
        transaksi_qs = transaksi_qs.filter(kategori_id=kategori_id)
    if tanggal_mulai:
        transaksi_qs = transaksi_qs.filter(tanggal__gte=tanggal_mulai)
    if tanggal_selesai:
        transaksi_qs = transaksi_qs.filter(tanggal__lte=tanggal_selesai)

    # Hitung total filter
    total_masuk_filtered = transaksi_qs.filter(jenis='masuk').aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')
    total_keluar_filtered = transaksi_qs.filter(jenis='keluar').aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')
    selisih_filtered = total_masuk_filtered - total_keluar_filtered

    # Pagination
    paginator = Paginator(transaksi_qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    kategori_list = KategoriTransaksi.objects.all()
    divisi_list = Divisi.objects.all()

    context = {
        'page_obj': page_obj,
        'kategori_list': kategori_list,
        'divisi_list': divisi_list,
        'total_masuk_filtered': total_masuk_filtered,
        'total_keluar_filtered': total_keluar_filtered,
        'selisih_filtered': selisih_filtered,
        'search': search,
        'jenis': jenis,
        'kategori_id': kategori_id,
        'tanggal_mulai': tanggal_mulai,
        'tanggal_selesai': tanggal_selesai,
    }
    return render(request, 'kas_app/transaksi_list.html', context)


def transaksi_create_view(request):
    if request.user.is_authenticated and hasattr(request.user, 'profil_anggota') and not request.user.is_staff:
        messages.error(request, "Akses ditolak. Anggota hanya dapat mengunggah bukti transfer kas.")
        return redirect('portal_anggota')

    if request.method == 'POST':
        jenis = request.POST.get('jenis')
        kategori_id = request.POST.get('kategori')
        nominal = request.POST.get('nominal', '0').replace('.', '').replace(',', '')
        judul = request.POST.get('judul', '').strip()
        keterangan = request.POST.get('keterangan', '').strip()
        tanggal = request.POST.get('tanggal') or timezone.now().date()
        divisi_id = request.POST.get('divisi_terkait') or None
        bukti_file = request.FILES.get('bukti_transaksi')

        try:
            kategori = KategoriTransaksi.objects.get(id=kategori_id)
            if kategori.is_iuran_kas:
                messages.error(
                    request,
                    "Pemasukan 'Iuran Kas Anggota' tidak dapat dicatat manual. "
                    "Iuran kas tercatat otomatis saat Admin meng-ACC bukti transfer anggota."
                )
                return redirect('transaksi_list')

            divisi = Divisi.objects.filter(id=divisi_id).first() if divisi_id else None

            transaksi = Transaksi.objects.create(
                jenis=jenis,
                kategori=kategori,
                nominal=Decimal(nominal),
                judul=judul,
                keterangan=keterangan,
                tanggal=tanggal,
                divisi_terkait=divisi,
                bukti_transaksi=bukti_file,
                dicatat_oleh=request.user if request.user.is_authenticated else None
            )
            messages.success(request, f"Transaksi operasional '{transaksi.judul}' senilai Rp {transaksi.nominal:,.0f} berhasil dicatat!")
        except Exception as e:
            messages.error(request, f"Gagal mencatat transaksi: {str(e)}")

        return redirect('transaksi_list')

    # Hanya tampilkan kategori operasional (bukan iuran kas anggota)
    kategori_list = KategoriTransaksi.objects.filter(is_iuran_kas=False)
    divisi_list = Divisi.objects.all()
    return render(request, 'kas_app/transaksi_form.html', {
        'kategori_list': kategori_list,
        'divisi_list': divisi_list,
        'action': 'Tambah',
        'today': timezone.now().date().strftime('%Y-%m-%d')
    })


def transaksi_update_view(request, pk):
    if request.user.is_authenticated and hasattr(request.user, 'profil_anggota') and not request.user.is_staff:
        messages.error(request, "Akses ditolak.")
        return redirect('portal_anggota')

    transaksi = get_object_or_404(Transaksi, pk=pk)
    if transaksi.kategori.is_iuran_kas:
        messages.error(request, "Transaksi iuran kas yang dihasilkan dari verifikasi (ACC) bukti transfer tidak dapat diedit manual.")
        return redirect('transaksi_list')

    if request.method == 'POST':
        try:
            kategori = KategoriTransaksi.objects.get(id=request.POST.get('kategori'))
            if kategori.is_iuran_kas:
                messages.error(request, "Kategori tidak dapat diubah ke Iuran Kas.")
                return redirect('transaksi_list')

            transaksi.jenis = request.POST.get('jenis')
            transaksi.kategori = kategori
            nominal_str = request.POST.get('nominal', '0').replace('.', '').replace(',', '')
            transaksi.nominal = Decimal(nominal_str)
            transaksi.judul = request.POST.get('judul', '').strip()
            transaksi.keterangan = request.POST.get('keterangan', '').strip()
            transaksi.tanggal = request.POST.get('tanggal')
            divisi_id = request.POST.get('divisi_terkait')
            transaksi.divisi_terkait = Divisi.objects.filter(id=divisi_id).first() if divisi_id else None

            if 'bukti_transaksi' in request.FILES:
                transaksi.bukti_transaksi = request.FILES['bukti_transaksi']

            transaksi.save()
            messages.success(request, f"Transaksi {transaksi.kode_transaksi} berhasil diperbarui.")
            return redirect('transaksi_list')
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan: {str(e)}")

    kategori_list = KategoriTransaksi.objects.filter(is_iuran_kas=False)
    divisi_list = Divisi.objects.all()
    return render(request, 'kas_app/transaksi_form.html', {
        'transaksi': transaksi,
        'kategori_list': kategori_list,
        'divisi_list': divisi_list,
        'action': 'Edit',
        'today': str(transaksi.tanggal)
    })


def transaksi_delete_view(request, pk):
    transaksi = get_object_or_404(Transaksi, pk=pk)
    if request.method == 'POST':
        kode = transaksi.kode_transaksi
        transaksi.delete()
        messages.success(request, f"Transaksi {kode} berhasil dihapus.")
        return redirect('transaksi_list')
    return render(request, 'kas_app/confirm_delete.html', {
        'obj': transaksi,
        'title': f'Hapus Transaksi {transaksi.kode_transaksi}',
        'cancel_url': 'transaksi_list'
    })


def transaksi_export_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="Laporan_Transaksi_Kas_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'

    # BOM for Excel Indonesian UTF-8 support
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Kode Transaksi', 'Tanggal', 'Jenis', 'Kategori', 'Judul Transaksi', 'Keterangan', 'Nominal (Rp)', 'Divisi Terkait', 'Dicatat Oleh'])

    transaksi_qs = Transaksi.objects.select_related('kategori', 'divisi_terkait', 'dicatat_oleh').all().order_by('-tanggal')
    for t in transaksi_qs:
        writer.writerow([
            t.kode_transaksi,
            t.tanggal.strftime('%d/%m/%Y'),
            'Pemasukan' if t.jenis == 'masuk' else 'Pengeluaran',
            t.kategori.nama if t.kategori else '-',
            t.judul,
            t.keterangan,
            f"{t.nominal:,.0f}".replace(',', '.'),
            t.divisi_terkait.nama if t.divisi_terkait else '-',
            t.dicatat_oleh.username if t.dicatat_oleh else '-'
        ])

    return response


# ==========================================
# IURAN KAS ANGGOTA & MATRIKS REKAPITULASI
# ==========================================
def iuran_matrix_view(request):
    profil = get_profil()
    tahun = int(request.GET.get('tahun', timezone.now().year))
    divisi_filter = request.GET.get('divisi', '')

    pastikan_periode_tahun(tahun)
    sinkronisasi_iuran_anggota(tahun)

    periode_list = PeriodeKas.objects.filter(tahun=tahun).order_by('bulan')
    anggota_qs = Anggota.objects.filter(status_aktif=True).select_related('divisi')

    if divisi_filter:
        anggota_qs = anggota_qs.filter(divisi_id=divisi_filter)

    # Ambil seluruh pengajuan iuran anggota pada tahun terkait
    pengajuan_qs = PengajuanIuran.objects.filter(
        periode__tahun=tahun
    ).select_related('periode', 'anggota').order_by('tanggal_pengajuan')

    # Mapping: (anggota_id, periode_id) -> objek PengajuanIuran terbaru
    pengajuan_dict = {}
    for pj in pengajuan_qs:
        pengajuan_dict[(pj.anggota_id, pj.periode_id)] = pj

    matrix_data = []
    total_kolom_bulan = {p.id: Decimal('0') for p in periode_list}

    for ag in anggota_qs:
        iuran_records = {i.periode_id: i for i in IuranKas.objects.filter(anggota=ag, periode__tahun=tahun)}
        bulan_status = []
        total_dibayar = Decimal('0')
        total_tunggakan = Decimal('0')
        bulan_nunggak_names = []

        for p in periode_list:
            record = iuran_records.get(p.id)
            pj = pengajuan_dict.get((ag.id, p.id))

            # Status 1: HIJAU (Lunas & Di-ACC Admin)
            if (record and record.status == 'lunas') or (pj and pj.status == 'disetujui'):
                nominal_bayar = record.nominal_dibayar if (record and record.nominal_dibayar > 0) else p.nominal
                tgl_bayar = record.tanggal_bayar if (record and record.tanggal_bayar) else (pj.diverifikasi_pada.date() if pj and pj.diverifikasi_pada else None)
                bukti_url = ""
                if pj and pj.bukti_transfer:
                    bukti_url = pj.bukti_transfer.url
                elif record and record.transaksi and record.transaksi.bukti_transaksi:
                    bukti_url = record.transaksi.bukti_transaksi.url

                bulan_status.append({
                    'periode_id': p.id,
                    'periode_nama': p.nama_periode,
                    'iuran_id': record.id if record else None,
                    'pengajuan_id': pj.id if pj else None,
                    'status': 'lunas',
                    'nominal': nominal_bayar,
                    'tanggal_bayar': tgl_bayar,
                    'bukti_url': bukti_url,
                    'metode': pj.metode_pembayaran if pj else (record.metode_pembayaran if record else 'Transfer Bank'),
                })
                total_dibayar += nominal_bayar
                total_kolom_bulan[p.id] += nominal_bayar

            # Status 2: KUNING (Menunggu ACC Admin)
            elif pj and pj.status == 'menunggu':
                bukti_url = pj.bukti_transfer.url if pj.bukti_transfer else ""
                bulan_status.append({
                    'periode_id': p.id,
                    'periode_nama': p.nama_periode,
                    'iuran_id': record.id if record else None,
                    'pengajuan_id': pj.id,
                    'status': 'menunggu',
                    'nominal': pj.nominal,
                    'tanggal_pengajuan': pj.tanggal_pengajuan,
                    'bukti_url': bukti_url,
                    'metode': pj.metode_pembayaran,
                    'catatan': pj.catatan,
                })
                total_tunggakan += p.nominal
                bulan_nunggak_names.append(p.nama_periode.split()[0])

            # Status 3: MERAH Ditolak (Bukti transfer ditolak oleh Admin)
            elif pj and pj.status == 'ditolak':
                bulan_status.append({
                    'periode_id': p.id,
                    'periode_nama': p.nama_periode,
                    'iuran_id': record.id if record else None,
                    'pengajuan_id': pj.id,
                    'status': 'ditolak',
                    'nominal': p.nominal,
                    'alasan_tolak': pj.catatan_bendahara or 'Bukti tidak valid atau nominal kurang',
                })
                total_tunggakan += p.nominal
                bulan_nunggak_names.append(p.nama_periode.split()[0])

            # Status 4: MERAH Belum Bayar (Belum kirim bukti TF sama sekali)
            else:
                bulan_status.append({
                    'periode_id': p.id,
                    'periode_nama': p.nama_periode,
                    'iuran_id': record.id if record else None,
                    'pengajuan_id': None,
                    'status': 'belum_bayar',
                    'nominal': p.nominal,
                })
                total_tunggakan += p.nominal
                bulan_nunggak_names.append(p.nama_periode.split()[0])

        # Generate WhatsApp reminder text
        wa_text = ""
        wa_url = ""
        if ag.no_hp and total_tunggakan > 0:
            daftar_bulan = ", ".join(bulan_nunggak_names[:3])
            if len(bulan_nunggak_names) > 3:
                daftar_bulan += f" dan {len(bulan_nunggak_names) - 3} bulan lainnya"

            pesan = (
                f"Halo {ag.nama},\n\n"
                f"Mengingatkan dari Bendahara {profil.nama_organisasi}.\n"
                f"Iuran kas ormawa untuk bulan ({daftar_bulan}) "
                f"dengan total tagihan sebesar *Rp {total_tunggakan:,.0f}* belum tercatat.\n\n"
                f"Silakan lakukan transfer dan kirimkan bukti transfer melalui portal kas ormawa ya. Terima kasih! 🙏"
            )
            wa_encoded = urllib.parse.quote(pesan)
            wa_url = f"https://wa.me/{ag.whatsapp_clean}?text={wa_encoded}"

        matrix_data.append({
            'anggota': ag,
            'bulan_status': bulan_status,
            'total_dibayar': total_dibayar,
            'total_tunggakan': total_tunggakan,
            'is_lunas_semua': total_tunggakan == 0,
            'wa_url': wa_url,
        })

    # Summary KPI
    grand_total_terkumpul = sum(row['total_dibayar'] for row in matrix_data)
    grand_total_tunggakan = sum(row['total_tunggakan'] for row in matrix_data)
    total_potensi_iuran = grand_total_terkumpul + grand_total_tunggakan
    persen_tercapai = round((grand_total_terkumpul / total_potensi_iuran * 100), 1) if total_potensi_iuran > 0 else 0

    # Periode footer summary
    summary_periode = []
    for p in periode_list:
        summary_periode.append({
            'periode': p,
            'total_terkumpul': total_kolom_bulan.get(p.id, Decimal('0'))
        })

    divisi_list = Divisi.objects.all()
    tahun_options = [2025, 2026, 2027]
    pending_count = PengajuanIuran.objects.filter(periode__tahun=tahun, status='menunggu').count()

    context = {
        'profil': profil,
        'tahun': tahun,
        'divisi_filter': divisi_filter,
        'divisi_list': divisi_list,
        'tahun_options': tahun_options,
        'periode_list': periode_list,
        'matrix_data': matrix_data,
        'summary_periode': summary_periode,
        'grand_total_terkumpul': grand_total_terkumpul,
        'grand_total_tunggakan': grand_total_tunggakan,
        'persen_tercapai': persen_tercapai,
        'pending_count': pending_count,
    }
    return render(request, 'kas_app/iuran_matrix.html', context)


def iuran_toggle_status(request, iuran_id):
    """Menolak bypass toggle iuran tanpa bukti transfer dari anggota."""
    messages.warning(
        request,
        "Iuran kas rutin tidak dapat diubah langsung secara manual. "
        "Status hanya berubah menjadi HIJAU jika anggota mengirimkan bukti transfer dan disetujui (ACC) oleh Admin."
    )
    return redirect('iuran_matrix')


def iuran_bayar_cepat(request):
    """Menolak bypass setor cepat tanpa bukti transfer anggota."""
    messages.warning(
        request,
        "Fitur setor manual dinonaktifkan. Setiap iuran kas wajib melalui pengunggahan bukti transfer oleh anggota "
        "dan verifikasi (ACC) oleh Admin."
    )
    return redirect('iuran_matrix')


def generate_periode_tahunan(request, tahun):
    pastikan_periode_tahun(tahun)
    sinkronisasi_iuran_anggota(tahun)
    messages.success(request, f"Periode kas tahun {tahun} berhasil diinisialisasi dan disinkronkan!")
    return redirect('iuran_matrix')


# ==========================================
# FITUR UNGGULAN: REKAPITULASI OTOMATIS
# ==========================================
def rekapitulasi_view(request):
    profil = get_profil()
    tahun = int(request.GET.get('tahun', timezone.now().year))
    pastikan_periode_tahun(tahun)

    # 1. Rekapitulasi Arus Kas Bulanan
    bulan_list = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
    ]

    rekap_bulanan = []
    saldo_berjalan = profil.saldo_awal

    total_tahunan_masuk = Decimal('0')
    total_tahunan_keluar = Decimal('0')

    for b_num, b_nama in bulan_list:
        saldo_awal_bulan = saldo_berjalan

        masuk_bulan = Transaksi.objects.filter(
            jenis='masuk',
            tanggal__year=tahun,
            tanggal__month=b_num
        ).aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')

        keluar_bulan = Transaksi.objects.filter(
            jenis='keluar',
            tanggal__year=tahun,
            tanggal__month=b_num
        ).aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')

        surplus_defisit = masuk_bulan - keluar_bulan
        saldo_berjalan = saldo_awal_bulan + surplus_defisit

        total_tahunan_masuk += masuk_bulan
        total_tahunan_keluar += keluar_bulan

        rekap_bulanan.append({
            'bulan_num': b_num,
            'bulan_nama': b_nama,
            'saldo_awal': saldo_awal_bulan,
            'pemasukan': masuk_bulan,
            'pengeluaran': keluar_bulan,
            'surplus_defisit': surplus_defisit,
            'saldo_akhir': saldo_berjalan,
        })

    saldo_akhir_tahun = saldo_berjalan
    surplus_defisit_tahunan = total_tahunan_masuk - total_tahunan_keluar

    # 2. Rekapitulasi Berdasarkan Kategori
    rekap_kategori_masuk = Transaksi.objects.filter(
        jenis='masuk',
        tanggal__year=tahun
    ).values('kategori__nama').annotate(
        total=Sum('nominal'),
        count=Count('id')
    ).order_by('-total')

    rekap_kategori_keluar = Transaksi.objects.filter(
        jenis='keluar',
        tanggal__year=tahun
    ).values('kategori__nama').annotate(
        total=Sum('nominal'),
        count=Count('id')
    ).order_by('-total')

    # 3. Rekapitulasi Anggaran Berdasarkan Divisi
    rekap_divisi = []
    for div in Divisi.objects.all():
        total_serapan = Transaksi.objects.filter(
            jenis='keluar',
            divisi_terkait=div,
            tanggal__year=tahun
        ).aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')

        total_iuran_div = IuranKas.objects.filter(
            anggota__divisi=div,
            periode__tahun=tahun,
            status='lunas'
        ).aggregate(Sum('nominal_dibayar'))['nominal_dibayar__sum'] or Decimal('0')

        rekap_divisi.append({
            'divisi': div,
            'serapan_pengeluaran': total_serapan,
            'iuran_terkumpul': total_iuran_div,
        })

    # 4. Kepatuhan Kas Anggota
    iuran_tahun = IuranKas.objects.filter(periode__tahun=tahun)
    total_lunas = iuran_tahun.filter(status='lunas').count()
    total_semua = iuran_tahun.count()
    persen_kepatuhan = round((total_lunas / total_semua * 100), 1) if total_semua > 0 else 0

    top_tunggakan = Anggota.objects.filter(
        status_aktif=True,
        iuran_list__periode__tahun=tahun,
        iuran_list__status='belum_lunas'
    ).annotate(
        jumlah_nunggak=Count('iuran_list'),
        nominal_nunggak=Sum('iuran_list__periode__nominal')
    ).order_by('-jumlah_nunggak', '-nominal_nunggak')[:10]

    context = {
        'profil': profil,
        'tahun': tahun,
        'rekap_bulanan': rekap_bulanan,
        'total_tahunan_masuk': total_tahunan_masuk,
        'total_tahunan_keluar': total_tahunan_keluar,
        'surplus_defisit_tahunan': surplus_defisit_tahunan,
        'saldo_akhir_tahun': saldo_akhir_tahun,
        'rekap_kategori_masuk': rekap_kategori_masuk,
        'rekap_kategori_keluar': rekap_kategori_keluar,
        'rekap_divisi': rekap_divisi,
        'persen_kepatuhan': persen_kepatuhan,
        'top_tunggakan': top_tunggakan,
        'tahun_options': [2025, 2026, 2027],
    }
    return render(request, 'kas_app/rekapitulasi.html', context)


def cetak_lpj_view(request):
    """Halaman Laporan Pertanggungjawaban (LPJ) Keuangan resmi siap cetak."""
    profil = get_profil()
    tahun = int(request.GET.get('tahun', timezone.now().year))
    bulan_awal = int(request.GET.get('bulan_awal', 1))
    bulan_akhir = int(request.GET.get('bulan_akhir', 12))

    tgl_awal = date(tahun, bulan_awal, 1)
    if bulan_akhir == 12:
        tgl_akhir = date(tahun, 12, 31)
    else:
        import calendar
        last_day = calendar.monthrange(tahun, bulan_akhir)[1]
        tgl_akhir = date(tahun, bulan_akhir, last_day)

    transaksi_masuk = Transaksi.objects.filter(
        jenis='masuk',
        tanggal__range=[tgl_awal, tgl_akhir]
    ).select_related('kategori', 'divisi_terkait').order_by('tanggal')

    transaksi_keluar = Transaksi.objects.filter(
        jenis='keluar',
        tanggal__range=[tgl_awal, tgl_akhir]
    ).select_related('kategori', 'divisi_terkait').order_by('tanggal')

    total_masuk = transaksi_masuk.aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')
    total_keluar = transaksi_keluar.aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')
    saldo_akhir = profil.saldo_awal + total_masuk - total_keluar

    # Kategori ringkasan
    kategori_summary = Transaksi.objects.filter(
        tanggal__range=[tgl_awal, tgl_akhir]
    ).values('jenis', 'kategori__nama').annotate(total=Sum('nominal')).order_by('jenis', '-total')

    context = {
        'profil': profil,
        'tahun': tahun,
        'tgl_awal': tgl_awal,
        'tgl_akhir': tgl_akhir,
        'transaksi_masuk': transaksi_masuk,
        'transaksi_keluar': transaksi_keluar,
        'total_masuk': total_masuk,
        'total_keluar': total_keluar,
        'saldo_akhir': saldo_akhir,
        'kategori_summary': kategori_summary,
        'tgl_cetak': timezone.now().strftime('%d %B %Y'),
    }
    return render(request, 'kas_app/cetak_lpj.html', context)


def rekap_bulanan_export_csv(request):
    tahun = int(request.GET.get('tahun', timezone.now().year))
    profil = get_profil()

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="Rekap_Arus_Kas_Bulanan_{tahun}.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow([f"REKAPITULASI ARUS KAS ORGANISASI KEMAHASISWAAN TAHUN {tahun}"])
    writer.writerow([f"Organisasi: {profil.nama_organisasi} - {profil.nama_institusi}"])
    writer.writerow([])
    writer.writerow(['Bulan', 'Saldo Awal (Rp)', 'Pemasukan (Rp)', 'Pengeluaran (Rp)', 'Surplus/Defisit (Rp)', 'Saldo Akhir (Rp)'])

    bulan_list = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
    ]

    saldo_berjalan = profil.saldo_awal
    tot_masuk = Decimal('0')
    tot_keluar = Decimal('0')

    for b_num, b_nama in bulan_list:
        saldo_awal_bln = saldo_berjalan
        m = Transaksi.objects.filter(jenis='masuk', tanggal__year=tahun, tanggal__month=b_num).aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')
        k = Transaksi.objects.filter(jenis='keluar', tanggal__year=tahun, tanggal__month=b_num).aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')
        diff = m - k
        saldo_berjalan = saldo_awal_bln + diff
        tot_masuk += m
        tot_keluar += k

        writer.writerow([
            b_nama,
            f"{saldo_awal_bln:,.0f}".replace(',', '.'),
            f"{m:,.0f}".replace(',', '.'),
            f"{k:,.0f}".replace(',', '.'),
            f"{diff:,.0f}".replace(',', '.'),
            f"{saldo_berjalan:,.0f}".replace(',', '.')
        ])

    writer.writerow([])
    writer.writerow([
        'TOTAL / SALDO AKHIR',
        '-',
        f"{tot_masuk:,.0f}".replace(',', '.'),
        f"{tot_keluar:,.0f}".replace(',', '.'),
        f"{(tot_masuk - tot_keluar):,.0f}".replace(',', '.'),
        f"{saldo_berjalan:,.0f}".replace(',', '.')
    ])

    return response


# ==========================================
# MANAJEMEN ANGGOTA
# ==========================================
def anggota_list_view(request):
    anggota_qs = Anggota.objects.select_related('divisi').all()

    search = request.GET.get('search', '').strip()
    divisi_id = request.GET.get('divisi', '').strip()
    status = request.GET.get('status', '').strip()

    if search:
        anggota_qs = anggota_qs.filter(
            Q(nama__icontains=search) |
            Q(nim__icontains=search) |
            Q(jabatan__icontains=search)
        )
    if divisi_id:
        anggota_qs = anggota_qs.filter(divisi_id=divisi_id)
    if status == 'aktif':
        anggota_qs = anggota_qs.filter(status_aktif=True)
    elif status == 'nonaktif':
        anggota_qs = anggota_qs.filter(status_aktif=False)

    paginator = Paginator(anggota_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    divisi_list = Divisi.objects.all()

    context = {
        'page_obj': page_obj,
        'divisi_list': divisi_list,
        'search': search,
        'divisi_id': divisi_id,
        'status': status,
        'total_anggota': Anggota.objects.count(),
        'total_aktif': Anggota.objects.filter(status_aktif=True).count(),
    }
    return render(request, 'kas_app/anggota_list.html', context)


def anggota_create_view(request):
    if request.method == 'POST':
        nim = request.POST.get('nim', '').strip()
        nama = request.POST.get('nama', '').strip()
        divisi_id = request.POST.get('divisi')
        jabatan = request.POST.get('jabatan', 'Staff').strip()
        angkatan = request.POST.get('angkatan', 2024)
        no_hp = request.POST.get('no_hp', '').strip()
        email = request.POST.get('email', '').strip()

        try:
            divisi = Divisi.objects.get(id=divisi_id)
            anggota = Anggota.objects.create(
                nim=nim,
                nama=nama,
                divisi=divisi,
                jabatan=jabatan,
                angkatan=int(angkatan),
                no_hp=no_hp,
                email=email,
                status_aktif=True
            )
            # Sinkronkan iuran tahun berjalan
            sinkronisasi_iuran_anggota(timezone.now().year)
            messages.success(request, f"Anggota '{anggota.nama}' ({anggota.nim}) berhasil ditambahkan!")
            return redirect('anggota_list')
        except Exception as e:
            messages.error(request, f"Gagal menambahkan anggota: {str(e)}")

    divisi_list = Divisi.objects.all()
    return render(request, 'kas_app/anggota_form.html', {
        'divisi_list': divisi_list,
        'action': 'Tambah'
    })


def anggota_update_view(request, pk):
    anggota = get_object_or_404(Anggota, pk=pk)
    if request.method == 'POST':
        try:
            anggota.nim = request.POST.get('nim', '').strip()
            anggota.nama = request.POST.get('nama', '').strip()
            anggota.divisi_id = request.POST.get('divisi')
            anggota.jabatan = request.POST.get('jabatan', 'Staff').strip()
            anggota.angkatan = int(request.POST.get('angkatan', 2024))
            anggota.no_hp = request.POST.get('no_hp', '').strip()
            anggota.email = request.POST.get('email', '').strip()
            anggota.status_aktif = 'status_aktif' in request.POST
            anggota.save()

            messages.success(request, f"Data anggota {anggota.nama} berhasil diperbarui.")
            return redirect('anggota_list')
        except Exception as e:
            messages.error(request, f"Gagal memperbarui anggota: {str(e)}")

    divisi_list = Divisi.objects.all()
    return render(request, 'kas_app/anggota_form.html', {
        'anggota': anggota,
        'divisi_list': divisi_list,
        'action': 'Edit'
    })


def anggota_delete_view(request, pk):
    anggota = get_object_or_404(Anggota, pk=pk)
    if request.method == 'POST':
        nama = anggota.nama
        anggota.delete()
        messages.success(request, f"Anggota {nama} berhasil dihapus.")
        return redirect('anggota_list')
    return render(request, 'kas_app/confirm_delete.html', {
        'obj': anggota,
        'title': f'Hapus Anggota: {anggota.nama}',
        'cancel_url': 'anggota_list'
    })


def anggota_detail_view(request, pk):
    anggota = get_object_or_404(Anggota, pk=pk)
    tahun = int(request.GET.get('tahun', timezone.now().year))
    pastikan_periode_tahun(tahun)
    sinkronisasi_iuran_anggota(tahun)

    iuran_list = IuranKas.objects.filter(anggota=anggota, periode__tahun=tahun).select_related('periode').order_by('periode__bulan')
    total_lunas = iuran_list.filter(status='lunas').aggregate(Sum('nominal_dibayar'))['nominal_dibayar__sum'] or Decimal('0')
    total_target = sum(i.periode.nominal for i in iuran_list)
    total_tunggakan = total_target - total_lunas

    context = {
        'anggota': anggota,
        'tahun': tahun,
        'iuran_list': iuran_list,
        'total_lunas': total_lunas,
        'total_tunggakan': total_tunggakan,
        'tahun_options': [2025, 2026, 2027],
    }
    return render(request, 'kas_app/anggota_detail.html', context)


# ==========================================
# PENGATURAN SISTEM & PROFIL
# ==========================================
def pengaturan_view(request):
    profil = get_profil()
    if request.method == 'POST':
        try:
            profil.nama_organisasi = request.POST.get('nama_organisasi', '').strip()
            profil.nama_institusi = request.POST.get('nama_institusi', '').strip()
            profil.singkatan = request.POST.get('singkatan', '').strip()
            profil.periode_kepengurusan = request.POST.get('periode_kepengurusan', '').strip()
            profil.nama_ketua = request.POST.get('nama_ketua', '').strip()
            profil.nim_ketua = request.POST.get('nim_ketua', '').strip()
            profil.nama_bendahara = request.POST.get('nama_bendahara', '').strip()
            profil.nim_bendahara = request.POST.get('nim_bendahara', '').strip()
            profil.nama_pembina = request.POST.get('nama_pembina', '').strip()
            profil.nip_pembina = request.POST.get('nip_pembina', '').strip()

            nom_str = request.POST.get('nominal_kas_wajib', '10000').replace('.', '').replace(',', '')
            profil.nominal_kas_wajib = Decimal(nom_str)

            saldo_str = request.POST.get('saldo_awal', '0').replace('.', '').replace(',', '')
            profil.saldo_awal = Decimal(saldo_str)

            profil.alamat_sekretariat = request.POST.get('alamat_sekretariat', '').strip()
            profil.email = request.POST.get('email', '').strip()
            profil.no_telepon = request.POST.get('no_telepon', '').strip()

            if 'logo' in request.FILES:
                profil.logo = request.FILES['logo']

            profil.save()
            messages.success(request, "Pengaturan profil organisasi berhasil disimpan!")
            return redirect('pengaturan')
        except Exception as e:
            messages.error(request, f"Gagal menyimpan pengaturan: {str(e)}")

    kategori_masuk = KategoriTransaksi.objects.filter(jenis='masuk')
    kategori_keluar = KategoriTransaksi.objects.filter(jenis='keluar')
    divisi_list = Divisi.objects.all()

    context = {
        'profil': profil,
        'kategori_masuk': kategori_masuk,
        'kategori_keluar': kategori_keluar,
        'divisi_list': divisi_list,
    }
    return render(request, 'kas_app/pengaturan.html', context)


def kategori_create_view(request):
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        jenis = request.POST.get('jenis', 'keluar')
        deskripsi = request.POST.get('deskripsi', '').strip()

        if nama:
            KategoriTransaksi.objects.create(
                nama=nama,
                jenis=jenis,
                deskripsi=deskripsi
            )
            messages.success(request, f"Kategori '{nama}' berhasil ditambahkan.")
    return redirect('pengaturan')


def kategori_delete_view(request, pk):
    kategori = get_object_or_404(KategoriTransaksi, pk=pk)
    if kategori.is_iuran_kas:
        messages.error(request, "Kategori sistem 'Iuran Kas Anggota' tidak dapat dihapus.")
        return redirect('pengaturan')

    if kategori.transaksi_list.exists():
        messages.error(request, f"Kategori '{kategori.nama}' tidak dapat dihapus karena sudah dipakai dalam transaksi.")
        return redirect('pengaturan')

    nama = kategori.nama
    kategori.delete()
    messages.success(request, f"Kategori '{nama}' berhasil dihapus.")
    return redirect('pengaturan')


# ==========================================
# AUTHENTICATION
# ==========================================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Selamat datang kembali, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            return redirect(next_url or 'dashboard')
        else:
            messages.error(request, "Username atau kata sandi salah. Silakan coba lagi.")

    return render(request, 'kas_app/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "Anda telah keluar dari sistem.")
    return redirect('login')


# ==========================================
# PORTAL ANGGOTA MAHASISWA & KIRIM BUKTI KAS
# ==========================================
def portal_anggota_view(request):
    profil = get_profil()
    current_year = timezone.now().year
    pastikan_periode_tahun(current_year)

    # Dapatkan objek Anggota yang sedang login, atau fallback anggota pertama untuk preview
    anggota = None
    if request.user.is_authenticated and hasattr(request.user, 'profil_anggota'):
        anggota = request.user.profil_anggota
    else:
        # Fallback untuk pengujian/preview
        anggota = Anggota.objects.filter(nim='2408101004').first() or Anggota.objects.first()

    sinkronisasi_iuran_anggota(current_year)

    # Iuran Anggota Terkait Tahun Ini
    iuran_list = IuranKas.objects.filter(
        anggota=anggota,
        periode__tahun=current_year
    ).select_related('periode').order_by('periode__bulan')

    total_lunas = iuran_list.filter(status='lunas').aggregate(Sum('nominal_dibayar'))['nominal_dibayar__sum'] or Decimal('0')
    total_target = sum(i.periode.nominal for i in iuran_list)
    total_tunggakan = total_target - total_lunas
    persen_lunas = round((total_lunas / total_target * 100), 1) if total_target > 0 else 0

    # Riwayat Pengajuan Bukti Pembayaran oleh Anggota Ini
    pengajuan_list = PengajuanIuran.objects.filter(anggota=anggota).select_related('periode').order_by('-tanggal_pengajuan')
    pengajuan_dict = {pj.periode_id: pj for pj in pengajuan_list}

    # Buat status visual per bulan untuk dashboard anggota (Hijau / Kuning / Merah)
    iuran_display_list = []
    periode_ids_sudah_diajukan_atau_lunas = set()

    for i in iuran_list:
        pj = pengajuan_dict.get(i.periode_id)
        if i.status == 'lunas':
            st = 'lunas'
            periode_ids_sudah_diajukan_atau_lunas.add(i.periode_id)
        elif pj and pj.status == 'menunggu':
            st = 'menunggu'
            periode_ids_sudah_diajukan_atau_lunas.add(i.periode_id)
        elif pj and pj.status == 'ditolak':
            st = 'ditolak'
        else:
            st = 'belum_lunas'

        iuran_display_list.append({
            'iuran': i,
            'status': st,
            'pengajuan': pj,
        })

    # Periode yang belum lunas dan belum ada pengajuan pending
    periode_belum_lunas = [
        i.periode for i in iuran_list
        if i.periode_id not in periode_ids_sudah_diajukan_atau_lunas
    ]

    # Transparansi Kas Ormawa (Read-Only)
    total_masuk = Transaksi.objects.filter(jenis='masuk').aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')
    total_keluar = Transaksi.objects.filter(jenis='keluar').aggregate(Sum('nominal'))['nominal__sum'] or Decimal('0')
    saldo_akhir_ormawa = profil.saldo_awal + total_masuk - total_keluar
    transaksi_terbaru = Transaksi.objects.select_related('kategori', 'divisi_terkait').all()[:6]

    context = {
        'profil': profil,
        'anggota': anggota,
        'current_year': current_year,
        'iuran_list': iuran_display_list,
        'total_lunas': total_lunas,
        'total_tunggakan': total_tunggakan,
        'persen_lunas': persen_lunas,
        'periode_belum_lunas': periode_belum_lunas,
        'pengajuan_list': pengajuan_list,
        'saldo_akhir_ormawa': saldo_akhir_ormawa,
        'total_masuk': total_masuk,
        'total_keluar': total_keluar,
        'transaksi_terbaru': transaksi_terbaru,
    }
    return render(request, 'kas_app/portal_anggota.html', context)


def kirim_bukti_iuran_view(request):
    """Memungkinkan anggota mengunggah struk/bukti transfer kas rutin."""
    if request.method == 'POST':
        periode_id = request.POST.get('periode_id')
        metode = request.POST.get('metode_pembayaran', 'Transfer Bank')
        catatan = request.POST.get('catatan', '').strip()
        bukti_file = request.FILES.get('bukti_transfer')

        # Tentukan siapa anggotanya
        if request.user.is_authenticated and hasattr(request.user, 'profil_anggota'):
            anggota = request.user.profil_anggota
        else:
            # Fallback untuk demo
            anggota_id = request.POST.get('anggota_id')
            anggota = Anggota.objects.filter(id=anggota_id).first() or Anggota.objects.first()

        try:
            periode = PeriodeKas.objects.get(id=periode_id)
            if not bukti_file:
                mock_rel_path = generate_mock_transfer_receipt(anggota, periode, metode, catatan)
                bukti_file = mock_rel_path if mock_rel_path else None

            pengajuan = PengajuanIuran.objects.create(
                anggota=anggota,
                periode=periode,
                nominal=periode.nominal,
                metode_pembayaran=metode,
                bukti_transfer=bukti_file,
                catatan=catatan,
                status='menunggu'
            )
            messages.success(
                request,
                f"Bukti pembayaran kas bulan {periode.nama_periode} berhasil dikirim ke Admin! "
                "Status di matriks kini KUNING (Menunggu ACC)."
            )
        except Exception as e:
            messages.error(request, f"Gagal mengirim bukti pembayaran: {str(e)}")

    return redirect('portal_anggota')


# ==========================================
# VERIFIKASI BUKTI BAYAR (PANEL BENDAHARA)
# ==========================================
def verifikasi_iuran_list_view(request):
    """Halaman bendahara untuk meninjau dan memverifikasi bukti bayar anggota."""
    if request.user.is_authenticated and hasattr(request.user, 'profil_anggota') and not request.user.is_staff:
        messages.error(request, "Akses ditolak. Fitur ini hanya untuk Admin/Bendahara.")
        return redirect('portal_anggota')

    status_filter = request.GET.get('status', 'menunggu')
    pengajuan_qs = PengajuanIuran.objects.select_related('anggota__divisi', 'periode').all()

    if status_filter in ['menunggu', 'disetujui', 'ditolak']:
        pengajuan_qs = pengajuan_qs.filter(status=status_filter)

    count_menunggu = PengajuanIuran.objects.filter(status='menunggu').count()
    count_disetujui = PengajuanIuran.objects.filter(status='disetujui').count()
    count_ditolak = PengajuanIuran.objects.filter(status='ditolak').count()

    context = {
        'pengajuan_list': pengajuan_qs,
        'status_filter': status_filter,
        'count_menunggu': count_menunggu,
        'count_disetujui': count_disetujui,
        'count_ditolak': count_ditolak,
    }
    return render(request, 'kas_app/verifikasi_iuran.html', context)


def verifikasi_iuran_action_view(request, pk):
    """Aksi menyetujui (ACC) atau menolak pengajuan bukti kas dari anggota."""
    if request.user.is_authenticated and hasattr(request.user, 'profil_anggota') and not request.user.is_staff:
        messages.error(request, "Akses ditolak.")
        return redirect('portal_anggota')

    pengajuan = get_object_or_404(PengajuanIuran, pk=pk)
    action = request.POST.get('action') # 'setujui' atau 'tolak'
    catatan_bendahara = request.POST.get('catatan_bendahara', '').strip()

    if action == 'setujui':
        # 1. Update status pengajuan
        pengajuan.status = 'disetujui'
        pengajuan.catatan_bendahara = catatan_bendahara or 'Bukti transfer valid dan telah di-ACC Admin.'
        pengajuan.diverifikasi_oleh = request.user if request.user.is_authenticated else None
        pengajuan.diverifikasi_pada = timezone.now()
        pengajuan.save()

        # 2. Update IuranKas anggota menjadi lunas
        iuran, _ = IuranKas.objects.get_or_create(
            anggota=pengajuan.anggota,
            periode=pengajuan.periode
        )
        iuran.status = 'lunas'
        iuran.nominal_dibayar = pengajuan.nominal
        iuran.tanggal_bayar = timezone.now().date()
        iuran.metode_pembayaran = pengajuan.metode_pembayaran

        # 3. Otomatis catat ke Transaksi Kas Masuk
        kat_iuran, _ = KategoriTransaksi.objects.get_or_create(
            nama='Iuran Kas Anggota',
            defaults={'jenis': 'masuk', 'is_iuran_kas': True, 'deskripsi': 'Penerimaan kas rutin wajib anggota'}
        )
        trx = Transaksi.objects.create(
            jenis='masuk',
            kategori=kat_iuran,
            nominal=pengajuan.nominal,
            judul=f"Kas Anggota: {pengajuan.anggota.nama} ({pengajuan.periode.nama_periode})",
            keterangan=f"Verifikasi transfer ({pengajuan.metode_pembayaran}) di-ACC oleh Admin. Catatan: {pengajuan.catatan or '-'}",
            tanggal=timezone.now().date(),
            divisi_terkait=pengajuan.anggota.divisi,
            bukti_transaksi=pengajuan.bukti_transfer,
            dicatat_oleh=request.user if request.user.is_authenticated else None
        )
        iuran.transaksi = trx
        iuran.save()

        messages.success(
            request,
            f"Bukti transfer {pengajuan.anggota.nama} ({pengajuan.periode.nama_periode}) BERHASIL DI-ACC! "
            f"Status di Matriks kini HIJAU (Lunas)."
        )

    elif action == 'tolak':
        pengajuan.status = 'ditolak'
        pengajuan.catatan_bendahara = catatan_bendahara or 'Bukti transfer tidak terbaca atau nominal tidak sesuai.'
        pengajuan.diverifikasi_oleh = request.user if request.user.is_authenticated else None
        pengajuan.diverifikasi_pada = timezone.now()
        pengajuan.save()

        messages.warning(
            request,
            f"Pengajuan bukti transfer dari {pengajuan.anggota.nama} ({pengajuan.periode.nama_periode}) telah DITOLAK."
        )

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'verifikasi_iuran_list')
