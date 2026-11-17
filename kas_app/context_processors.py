from .models import ProfilOrganisasi, PengajuanIuran, Anggota

def profil_organisasi_processor(request):
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
            nominal_kas_wajib=10000,
            periode_kas='bulanan',
            saldo_awal=500000
        )

    is_bendahara = True
    is_anggota = False
    user_anggota = None

    if request.user.is_authenticated:
        if hasattr(request.user, 'profil_anggota') and not request.user.is_staff:
            is_bendahara = False
            is_anggota = True
            user_anggota = request.user.profil_anggota
        else:
            is_bendahara = True
            is_anggota = False

    pending_pengajuan_count = PengajuanIuran.objects.filter(status='menunggu').count() if is_bendahara else 0

    return {
        'profil_organisasi': profil,
        'app_title': 'SIMKAS ORMAWA',
        'app_subtitle': 'Sistem Informasi Manajemen Kas Organisasi Kemahasiswaan Berbasis Web dengan Fitur Rekapitulasi Otomatis',
        'is_bendahara': is_bendahara,
        'is_anggota': is_anggota,
        'user_anggota': user_anggota,
        'pending_pengajuan_count': pending_pengajuan_count,
    }
