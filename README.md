# E-Voting Ketua OSIS — Modern UI

## Desain dan kemudahan penggunaan
- Sidebar navigasi dengan menu yang jelas.
- Dashboard ringkasan kandidat, pemilih, suara masuk, dan belum memilih.
- Form tambah kandidat/pemilih dalam jendela terpisah.
- Pencarian data kandidat dan pemilih.
- Konfirmasi sebelum suara disimpan.
- Rekap suara serta ekspor PDF/Excel.
- Pengaturan status pemilihan dan backup SQL.

## Instalasi
1. Jalankan MySQL dari XAMPP.
2. Buka `http://localhost/phpmyadmin`.
3. Import `database/e_voting_osis.sql`.
4. Buka terminal pada folder project:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

## Login awal
- Username: `admin`
- Password: `admin123`

## Catatan
Konfigurasi database ada di bagian `DB_CONFIG` pada `main.py`.
Aplikasi ini dibuat sebagai proyek pembelajaran. Untuk pemilihan resmi, perlu ditambah audit log, autentikasi akun pemilih individual, pengamanan server, dan pemeriksaan independen.
