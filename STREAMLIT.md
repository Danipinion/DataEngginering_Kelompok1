# 🔮 Dokumentasi Simulator Prediksi Streamlit

Aplikasi web interaktif ini dikembangkan menggunakan **Streamlit** sebagai antarmuka pengguna (UI) untuk menjalankan simulator prediksi Machine Learning secara langsung dari model Random Forest Regressor yang telah dilatih. Untuk visualisasi dan analisis data secara mendalam, proyek ini menggunakan **Looker Studio**.

---

## 📁 Integrasi Clean Architecture

Mengikuti prinsip arsitektur bersih, file presentation layer dipisahkan dan dihubungkan secara modular:

- **Presentation Layer (`app.py`)**: Bertanggung jawab penuh atas tampilan antarmuka, penanganan slider input untuk memanipulasi variabel, dan penampilan hasil estimasi fatalitas risiko wilayah.
- **Configuration Layer (`config/settings.py`)**: Menyediakan konfigurasi terpusat untuk lokasi model (`models/`), dataset proses (`data/processed/`), nama tabel, serta URI database tanpa hardcoding kredensial.
- **Infrastructure/Data Layer (`src/database.py`)**: Digunakan kembali oleh `app.py` untuk mengambil data statistik dari server cloud Aiven PostgreSQL dengan fungsi `fetch_from_db` guna mengkalibrasi batas minimum, maksimum, dan median dari slider parameter input.

### 🛡️ Fitur Ketahanan Sistem (Resilience & Fallback)

Untuk memastikan demo/presentasi simulator tetap berjalan lancar dalam kondisi apa pun (misalnya saat koneksi internet terputus atau Aiven DB offline):

1. **Koneksi Cloud PostgreSQL (Prioritas Utama)**: Aplikasi mencoba memuat data kalibrasi langsung dari server Aiven PostgreSQL.
2. **Fallback Otomatis**: Jika database tidak dapat dijangkau, aplikasi akan secara otomatis memuat file cadangan lokal `data/processed/data_polda_jateng_cleaned.csv` untuk mengkalibrasi slider parameter input, dan menampilkan status **"Penyimpanan CSV Lokal (Offline)"** di sidebar.

---

## 🚀 Cara Menjalankan Aplikasi

1. **Aktifkan Virtual Environment**:

   ```bash
   source .venv/bin/activate
   ```

2. **Instalasi Dependency**:
   Pastikan Anda telah menginstal `streamlit` yang sudah tercantum di file `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan Aplikasi**:
   Eksekusi perintah berikut di terminal root proyek Anda:
   ```bash
   streamlit run app.py
   ```

---

## ⚙️ Fitur Utama Antarmuka

Aplikasi menyajikan antarmuka simulator berbasis slider masukan untuk memanipulasi variabel:

- **Volume Kendaraan**: Jumlah Sepeda Motor, Truk, Mobil Penumpang, dan Bus.
- **Kondisi Infrastruktur Jalan (KM)**: Jalan Kondisi Baik, Sedang, Rusak, dan Rusak Berat.
- **Faktor Cuaca**: Rata-rata Suhu (°C), Kelembaban (%), Curah Hujan (mm), dan Jumlah Hari Hujan.

Tombol **"Hitung Estimasi Fatalitas Risiko Wilayah"** memicu prediksi real-time menggunakan model _Random Forest Regressor_ (`random_forest_polda.pkl`) dan menampilkan estimasi jumlah korban meninggal dunia per tahun.
