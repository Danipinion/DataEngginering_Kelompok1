# Alur Kerja & Dokumentasi Pipeline

Dokumen ini menjelaskan alur kerja teknis, struktur folder, persiapan lingkungan, serta detail dari masing-masing fase pipeline Data Engineering & Machine Learning untuk proyek Polda Jawa Tengah.

## 📁 Struktur Folder

```
DataEngginering_Kelompok1/
├── config/
│   ├── __init__.py
│   └── settings.py          # Konfigurasi parameter model, fitur, dan path folder
├── data/
│   ├── raw/                 # Tempat menyimpan file CSV mentah (BPS)
│   └── processed/           # Tempat menyimpan dataset hasil pembersihan (.csv)
├── models/                  # Folder hasil training model (.pkl)
├── src/
│   ├── __init__.py
│   ├── ingestion.py         # Membaca data mentah dari CSV
│   ├── preprocessing.py     # Pembersihan, penyelarasan indeks, penggabungan, dan imputasi
│   ├── database.py          # Manajemen koneksi, unggah, dan unduh ke Aiven PostgreSQL
│   └── training.py          # Pemisahan data, training Random Forest, dan evaluasi model
├── .env.example             # Contoh File konfigurasi kredensial
├── main.py                  # Orkestrator utama pipeline
├── requirements.txt         # Daftar dependency package
└── README.md                # Dokumentasi Latar Belakang & Deskripsi Proyek
```

## 🛠️ Persiapan Environment

1. **Buat Virtual Environment (Opsional tapi direkomendasikan):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Untuk Linux/macOS
   # atau
   venv\Scripts\activate     # Untuk Windows
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Kredensial Database (.env):**
   Kredensial Aiven PostgreSQL diatur di dalam file `.env`:

   ```env
   AIVEN_DATABASE_URI=postgresql://avnadmin:[EMAIL_ADDRESS]:10561/defaultdb?sslmode=require
   ```

4. **Siapkan Data Mentah (Raw Data):**
   Letakkan file CSV berikut ke dalam folder `data/raw/`:
   - `Jumlah Korban Kecelakaan Lalu Lintas di Wilayah Polda Jawa Tengah Tahun, 2020.csv`
   - `Jumlah Kendaraan Bermotor Menurut Kabupaten_Kota dan Jenis Kendaraan di Provinsi Jawa Tengah, 2020.csv`
   - `Panjang Jalan Menurut Kabupaten_Kota dan Kondisi Jalan  di Provinsi Jawa Tengah (km), 2020.csv`
   - `Rata-Rata Suhu Udara, Kelembaban, Tekanan Udara, Kecepatan Angin, Curah Hujan, dan Penyinaran Matahari Menurut Stasiun di Provinsi Jawa Tengah, 2020.csv`

## 🚀 Cara Menjalankan Pipeline

Anda dapat menjalankan pipeline menggunakan `main.py` dengan beberapa argumen/flag:

1. **Jalankan Pipeline Lengkap (End-to-End dengan DB Upload):**

   ```bash
   python main.py
   ```

   _Alur:_ Membaca CSV mentah → Membersihkan & Menggabungkan → Upload ke database Aiven → Tarik kembali dari database → Training model & Evaluasi → Simpan model `.pkl` ke folder `models/`.

2. **Jalankan secara Lokal Saja (Tanpa Interaksi Database):**
   Jika Anda sedang tidak terkoneksi ke internet atau ingin mendemokan proses lokal dengan cepat:

   ```bash
   python main.py --local-only
   ```

   _Alur:_ Membaca CSV mentah → Membersihkan & Menggabungkan → Training model & Evaluasi secara lokal → Simpan model `.pkl`.

3. **Jalankan Pipeline dan Lewati Proses Upload Database:**
   ```bash
   python main.py --skip-upload
   ```

## 📊 Alur Kerja & Penjelasan untuk Presentasi

Saat melakukan presentasi, Anda bisa menjelaskan 5 fase utama pipeline ini:

1. **Data Ingestion (`src/ingestion.py`):**
   Masing-masing file CSV dari BPS dibaca secara independen. Di fase ini, kita melakukan pembersihan awal seperti melompati baris judul yang berantakan (`skiprows`), menghapus nomor urut di awal nama kota (`1. Cilacap` menjadi `Cilacap`), dan membuang baris total provinsi.
2. **Data Preprocessing & Merging (`src/preprocessing.py`):**
   - **Penyelarasan Indeks:** Menyelaraskan nama Kabupaten/Kota dari data kondisi jalan agar tepat berpasangan dengan data kecelakaan.
   - **Merge (Penggabungan):** Menggabungkan tabel Kecelakaan, Kendaraan, dan Jalan secara _outer join_ berdasarkan nama Kabupaten/Kota.
   - **Pengolahan Cuaca:** Karena data cuaca dicatat per stasiun BMKG dan satu kota bisa memiliki lebih dari satu stasiun, data cuaca dikelompokkan (`groupby`) berdasarkan Kabupaten/Kota dan dihitung rata-ratanya (`mean`). Penggabungan menggunakan kunci pencocokan berbasis huruf kecil (`lowercase matching key`) untuk menghindari ketidakcocokan karakter.
   - **Imputasi & Casting:** Mengubah kolom jumlah menjadi tipe integer, menghapus kolom kosong seperti `angin_min`, dan mengisi nilai kosong (NaN) di data cuaca dengan nilai median masing-masing kolom.

3. **Database Layer (`src/database.py`):**
   Data yang telah bersih diunggah ke cloud database **Aiven PostgreSQL** (`data_polda_jateng`) dengan skema yang bersih dan tipe data yang terstandarisasi. Ini berguna sebagai _Single Source of Truth_ untuk tim analitik atau visualisasi (misal Streamlit / PowerBI).

4. **Model Training & Evaluation (`src/training.py`):**
   - Menarik data bersih dari database.
   - Memisahkan data menjadi set Training (80%) dan Testing (20%).
   - Melakukan training menggunakan algoritma **Random Forest Regressor** dengan target memprediksi jumlah korban meninggal (`korban_meninggal`).
   - Evaluasi model menggunakan metrik **MAE** dan **R2 Score**.

5. **Model Serialization:**
   Model disimpan menjadi `random_forest_polda.pkl` dan fitur-fitur disimpan menjadi `model_features.pkl` di folder `models/` agar siap digunakan langsung oleh aplikasi visualisasi/dashboard (Streamlit).
