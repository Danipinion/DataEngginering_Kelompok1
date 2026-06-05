import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# Database
AIVEN_DATABASE_URI = os.getenv("AIVEN_DATABASE_URI", "")
TABLE_NAME = "data_polda_jateng"

# Folder Structure Paths
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
MODEL_DIR = BASE_DIR / "models"

# Ensure essential directories are automatically created
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Dataset Filenames (Raw inputs)
FILE_KECELAKAAN = "Jumlah Korban Kecelakaan Lalu Lintas di Wilayah Polda Jawa Tengah Tahun, 2020.csv"
FILE_KENDARAAN = "Jumlah Kendaraan Bermotor Menurut Kabupaten_Kota dan Jenis Kendaraan di Provinsi Jawa Tengah, 2020.csv"
FILE_JALAN = "Panjang Jalan Menurut Kabupaten_Kota dan Kondisi Jalan  di Provinsi Jawa Tengah (km), 2020.csv"
FILE_CUACA = "Rata-Rata Suhu Udara, Kelembaban, Tekanan Udara, Kecepatan Angin, Curah Hujan, dan Penyinaran Matahari Menurut Stasiun di Provinsi Jawa Tengah, 2020.csv"

# Machine Learning Target & Features Config
FEATURES = [
    'mobil_penumpang', 'bus', 'truk', 'sepeda_motor',
    'jalan_kondisi_baik', 'jalan_kondisi_sedang', 'jalan_kondisi_rusak', 'jalan_kondisi_rusak_berat',
    'suhu_avg', 'kelembaban_avg', 'curah_hujan', 'hari_hujan'
]
TARGET = 'korban_meninggal'
