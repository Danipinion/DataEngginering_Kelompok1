# Analisis dan Prediksi Hubungan antara Kecelakaan Lalu Lintas, Volume Kendaraan, Kondisi Jalan, dan Faktor Cuaca di Provinsi Jawa Tengah Tahun 2020

## Kontributor

| Nama Lengkap                 | NIM        | Peran           |
| ---------------------------- | ---------- | --------------- |
| Habib Hajid Taqiudin         | 2443111043 | Project Manager |
| Mohammad Dani Taufiqurrohman | 2443111048 | Data Engineer   |
| Novandy Triarto Wahyono      | 2443111053 | Data Analyst    |

---

## Deskripsi Proyek

Proyek ini dikembangkan untuk menganalisis korelasi antara tingkat fatalitas kecelakaan lalu lintas (korban meninggal), volume kendaraan bermotor, kondisi infrastruktur jalan, dan faktor rata-rata cuaca di 35 Kabupaten/Kota di Provinsi Jawa Tengah pada tahun 2020. Data diekstraksi dari file publikasi resmi BPS Jawa Tengah dan BMKG, dibersihkan dan diintegrasikan menggunakan Python (Pandas), kemudian dimigrasikan ke database PostgreSQL cloud (Aiven) sebagai _Single Source of Truth_. Terakhir, data tersebut digunakan untuk melatih model Machine Learning Random Forest Regressor guna memprediksi jumlah korban meninggal.

---

## Manfaat Data

- **Tujuan Proyek:** Proyek ini bertujuan untuk membangun pipeline data otomatis dan terstruktur yang mengintegrasikan data lalu lintas, infrastruktur, dan cuaca di Jawa Tengah, guna menghasilkan wawasan prediktif dan model machine learning mengenai fatalitas kecelakaan.
- **Manfaat:**
  - **Kebijakan Transportasi:** Memberikan rekomendasi berbasis data bagi Polda Jateng dan Dinas Perhubungan dalam memetakan daerah rawan kecelakaan.
  - **Prioritas Infrastruktur:** Membantu Dinas Pekerjaan Umum dalam memprioritaskan perbaikan jalan berdasarkan dampaknya terhadap keselamatan jalan raya.
  - **Penelitian & Akademis:** Menjadi referensi integrasi data multi-sumber (iklim, infrastruktur, transportasi) untuk analisis keselamatan publik.
  - **Praktik Data Engineering:** Memberikan contoh penerapan nyata arsitektur ETL terpisah dan penyimpanan cloud relasional.

---

## Serving Analisis

Analisis data dan visualisasi interaktif (seperti grafik korelasi jalan rusak terhadap fatalitas dan peta sebaran kerawanan) disajikan menggunakan platform **Looker Studio** yang langsung terhubung ke database PostgreSQL Aiven.

---

## Serving Machine Learning

Model Machine Learning yang dikembangkan dilatih untuk memprediksi jumlah korban meninggal (`korban_meninggal`) berdasarkan fitur-fitur kendaraan, jalan, dan cuaca. Model ini diekspor ke dalam bentuk serialized file `.pkl` (`random_forest_polda.pkl` & `model_features.pkl`) di dalam folder `models/`. File ini disajikan melalui aplikasi **Streamlit** (yang dapat dijalankan dengan `app.py`) sebagai simulator prediksi tingkat fatalitas korban berdasarkan masukan parameter wilayah secara real-time. Detail penjelasan aplikasi web ini dapat diakses di **[STREAMLIT.md](STREAMLIT.md)**.

---

## Pipeline

### 1. Extract (Pengambilan Data)

- **Sumber Data:**
  - Data Korban Kecelakaan Lalu Lintas Polda Jateng 2020 (BPS)
  - Data Jumlah Kendaraan Bermotor menurut Kabupaten/Kota dan Jenis Kendaraan di Provinsi Jawa Tengah 2020 (BPS)
  - Data Panjang Jalan menurut Kabupaten/Kota dan Kondisi Jalan di Provinsi Jawa Tengah 2020 (BPS)
  - Data Rata-Rata Suhu Udara, Kelembaban, Curah Hujan, dll menurut Stasiun BMKG di Provinsi Jawa Tengah 2020 (BMKG)
- **Metode Pengambilan:**
  - File data mentah diunduh dalam format CSV dari portal data resmi BPS Jawa Tengah dan stasiun BMKG.
  - Data disimpan secara lokal di dalam direktori `data/raw/` sebelum masuk ke proses pengolahan.

### 2. Transform (Pembersihan & Transformasi)

- **Pembersihan:**
  - Melompati baris judul atas yang tidak beraturan (`skiprows`) dan membuang baris akumulasi total provinsi.
  - Menghapus prefiks nomor urut di awal nama Kabupaten/Kota (misal: `1. Cilacap` diubah menjadi `Cilacap`) dan merapikan spasi.
  - Membuang kolom yang tidak relevan atau kosong secara keseluruhan (seperti kolom `angin_min`).
  - Menangani nilai kosong (missing value) pada kolom cuaca dengan imputasi nilai median masing-masing kolom untuk mempertahankan jumlah baris data.
  - Mengubah kolom bertipe desimal yang berupa teks menjadi tipe numerik (`float`) dan kolom jumlah menjadi integer (`int64`).
- **Transformasi:**
  - Melakukan agregasi rata-rata data cuaca (`groupby().mean()`) per Kabupaten/Kota karena satu wilayah bisa memiliki beberapa stasiun BMKG.
  - Membuat kunci pencocokan yang seragam (`Kunci_Cocok`) dengan mengubah teks menjadi huruf kecil (_lowercase_), menghapus kata "Kabupaten " dan "Kota ", serta merapikan spasi di ujung nama untuk memastikan akurasi proses penggabungan (_merge/join_).
  - Menyatukan seluruh dataset secara _outer/left join_ dan menyelaraskan penamaan kolom ke format standar `snake_case`.

### 3. Load (Pemindahan ke Target)

- **Target:** Database PostgreSQL Cloud di hosting **Aiven**.
- **Skema Database:**
  - Tabel Target: `data_polda_jateng`
  - Skema Kolom utama: `kabupaten_kota`, `korban_meninggal`, `korban_luka_berat`, `korban_luka_ringan`, `mobil_penumpang`, `bus`, `truk`, `sepeda_motor`, `jumlah_kendaraan`, `jalan_kondisi_baik`, `jalan_kondisi_sedang`, `jalan_kondisi_rusak`, `jalan_kondisi_rusak_berat`, `suhu_avg`, `kelembaban_avg`, `curah_hujan`, `hari_hujan`, `penyinaran_matahari`.
- **Proses Load:**
  - Data hasil pembersihan diekspor ke local storage `data/processed/data_polda_jateng_cleaned.csv` sebagai pencadangan.
  - Upload data ke database menggunakan library `SQLAlchemy` dengan metode `to_sql` menggunakan opsi `if_exists='replace'` dan skema transaksi aman.
- **Penanganan Duplikasi & Integritas Data:**
  - Pengecekan tipe data secara ketat dilakukan pada tingkat Pandas sebelum data dimigrasikan ke PostgreSQL.
  - Validasi skema kolom sebelum eksekusi insert untuk mencegah kegagalan migrasi di server database cloud.

---

## Arsitektur/Workflow ETL

- **Alur Modular:** Program dirancang menggunakan pola **Clean Architecture** yang modular. Setiap fase diisolasi dalam file skrip mandiri agar program bersifat _reusable_, mudah dikelola, dan memiliki alur presentasi yang jelas.
- **Teknologi yang Digunakan:**
  - **ETL & Database:** Python, Pandas, Numpy, SQLAlchemy, Psycopg2-binary, Python-dotenv
  - **Machine Learning:** Scikit-learn (RandomForestRegressor, train_test_split, metrics), Joblib
  - **Visualisasi & Serving (Rencana/Opsional):** Streamlit, Matplotlib, Seaborn

---

## Kode Program

### Struktur Kode:

```
├── config/
│   └── settings.py          # Konfigurasi parameter model, fitur, dan path folder
├── src/
│   ├── ingestion.py         # Ekstraksi dan pembacaan data mentah (.csv)
│   ├── preprocessing.py     # Logika pembersihan, merging, dan imputasi median
│   ├── database.py          # Logika koneksi dan query upload/fetch database Aiven
│   └── training.py          # Logika training, evaluasi, dan ekspor model Random Forest
├── app.py                   # Presentation layer / Dashboard Web Streamlit & Simulator
└── main.py                  # Orchestrator utama untuk menjalankan pipeline
```

### Machine Learning:

- Menggunakan algoritma **Random Forest Regressor** dengan metrik evaluasi berupa **Mean Absolute Error (MAE)** untuk mengukur rata-rata selisih prediksi dan **R2 Score** untuk mengukur variabilitas target yang dapat dijelaskan oleh fitur prediktor.

---

## 🚀 Panduan Menjalankan Program

* **Pipeline Data (ETL & ML Training):** Cara melakukan instalasi dan menjalankan pipeline data secara lengkap tercantum di **[WORKFLOW.md](WORKFLOW.md)**.
* **Dashboard Visualisasi & Simulator (Streamlit):** Cara menjalankan dashboard web interaktif secara lengkap tercantum di **[STREAMLIT.md](STREAMLIT.md)**.
