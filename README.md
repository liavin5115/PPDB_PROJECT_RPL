# 📚 SISTEM PENERIMAAN PESERTA DIDIK BARU (PPDB) ONLINE

Sebuah sistem informasi berbasis web untuk pengelolaan penerimaan peserta didik baru yang dibangun menggunakan Flask dan SQLite.

**Developer:** Rafa Satria Isyo Pratama

## 🖥️ Screenshots

### Landing Page
![Landing Page 1](static/img/landing_page_1.png)
*Halaman utama website PPDB Online*

![Landing Page 2](static/img/landing_page_2.png)
*Bagian informasi program keahlian dan jalur pendaftaran*

### Halaman Login & Register
![Halaman Login](static/img/login.png)
*Halaman login pengguna*

![Halaman Register](static/img/register.png)
*Halaman pendaftaran akun baru*

### Dashboard Siswa
![Dashboard Siswa](static/img/dashboard_user.html.png)
*Dashboard untuk siswa dengan status pendaftaran*

![Dashboard Siswa 2](static/img/dashboard_user_2.png)
*Panel kelengkapan dokumen dan status pembayaran*

### Formulir Pendaftaran
![Formulir Pendaftaran](static/img/formulir_pendaftaran.png)
*Form pengisian data pendaftaran siswa*

### Dashboard Admin
![Dashboard Admin](static/img/admin_dashboard.png)
*Dashboard admin dengan grafik statistik*

![Dashboard Admin 2](static/img/admin_dashboard_2.png)
*Panel monitoring pendaftaran*

### Detail Pendaftaran
![Detail Pendaftaran](static/img/detail_student.png)
*Halaman detail data pendaftaran siswa*

### Tabel Data Pendaftar
![Tabel Pendaftar](static/img/table.png)
*Tabel lengkap data seluruh pendaftar*

## ✨ Fitur Utama

### 👨‍🎓 Fitur Siswa
- **Pendaftaran & Login**
  - Registrasi akun baru
  - Login dengan username dan password
  - Manajemen profil pengguna

- **Pengisian Formulir**
  - Form pendaftaran online
  - Upload dokumen persyaratan
  - Preview dokumen yang diupload
  - Edit data pendaftaran

- **Tracking Status**
  - Status verifikasi dokumen
  - Progress kelengkapan berkas
  - Status pembayaran
  - Notifikasi update status

### 👨‍💼 Fitur Admin
- **Manajemen Pendaftaran**
  - Dashboard dengan statistik real-time
  - Grafik visualisasi data pendaftar
  - Tabel data seluruh pendaftar
  - Filter dan pencarian data

- **Verifikasi & Validasi**
  - Verifikasi dokumen pendaftar
  - Validasi data siswa
  - Approval/Reject pendaftaran
  - Verifikasi pembayaran

- **Laporan & Analytics**
  - Grafik trend pendaftaran
  - Statistik per jurusan
  - Distribusi jenis kelamin
  - Export data ke Excel

## 🛠️ Tech Stack

### Backend
- **Python Flask** - Web framework
- **SQLite** - Database
- **SQLAlchemy** - ORM
- **Flask-Login** - Autentikasi
- **Flask-Migrate** - Migrasi database

### Frontend
- **Bootstrap 5** - Framework CSS
- **Chart.js** - Visualisasi data
- **DataTables** - Tabel interaktif
- **Bootstrap Icons** - Icon pack

### Tools & Library
- **Flask-WTF** - Form handling & validasi
- **Werkzeug** - Password hashing
- **Python-dotenv** - Environment variables

## 🚀 Instalasi & Setup

1. **Clone repository**
```powershell
git clone https://github.com/liavin5115/PPDB_PROJECT_RPL.git
cd PPDB_PROJECT_RPL
```

2. **Buat dan aktifkan virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Inisialisasi database**
```powershell
flask db upgrade
```

5. **Buat user admin**
```powershell
flask create-admin admin password123
```

6. **Jalankan aplikasi**
```powershell
flask run
```

Buka `http://localhost:5000` di browser Anda

## 📁 Struktur Project
```
PROJECT_PMB_SISWA/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── routes/
│   │   ├── auth.py         # Authentication routes
│   │   └── main.py         # Main application routes
│   ├── static/
│   │   ├── css/            # Style files
│   │   ├── js/             # JavaScript files
│   │   └── img/            # Image assets
│   └── templates/
│       ├── admin/          # Admin templates
│       ├── components/     # Reusable components
│       └── modals/         # Modal templates
├── migrations/              # Database migrations
├── config.py               # Application configuration
└── run.py                  # Application entry point
```

## 📚 Dokumentasi Lengkap

Dokumentasi lengkap dapat ditemukan di folder `docs/`:

- [Manual Pengguna](docs/USER_MANUAL.md) - Panduan lengkap penggunaan sistem
- [Changelog](docs/CHANGELOG.md) - Riwayat perubahan dan update sistem

Silakan baca dokumentasi tersebut untuk informasi lebih detail tentang penggunaan sistem dan riwayat perubahannya.

## 📧 Kontak & Dukungan

**Developer:** Rafa Satria Isyo Pratama
- GitHub: [liavin5115](https://github.com/liavin5115)
- Email: rafa.satria.isyo.pratama.2008@gmail.com

## 📝 Lisensi

Project ini dilisensikan di bawah Lisensi MIT.

---
Dibuat dengan ❤️ oleh Rafa Satria Isyo Pratama
