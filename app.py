import streamlit as st
import pandas as pd
import numpy as np
import joblib
from config import settings
from src.database import fetch_from_db

# Page Configuration
st.set_page_config(
    page_title="Polda Jateng Safety Predictor",
    page_icon="🔮",
    layout="wide"
)

# ==============================================================================
# DATABASE & MODEL LOADER
# ==============================================================================
@st.cache_data
def load_data():
    """Loads cleaned data from Aiven Cloud PostgreSQL or falls back to local CSV to calibrate sliders."""
    if settings.AIVEN_DATABASE_URI:
        try:
            df = fetch_from_db(settings.TABLE_NAME, settings.AIVEN_DATABASE_URI)
            return df, "Aiven PostgreSQL Cloud Database"
        except Exception as e:
            st.sidebar.warning(f"⚠️ Gagal menghubungkan ke Aiven DB: {e}. Menggunakan data lokal.")
    
    # Fallback to local CSV
    local_path = settings.PROCESSED_DATA_DIR / "data_polda_jateng_cleaned.csv"
    if local_path.exists():
        df = pd.read_csv(local_path)
        return df, "Penyimpanan CSV Lokal (Offline)"
    else:
        st.sidebar.error("❌ Data tidak ditemukan. Silakan jalankan 'python main.py' terlebih dahulu.")
        return None, None

@st.cache_resource
def load_ml_model():
    """Loads the serialized Random Forest model and its trained features."""
    model_path = settings.MODEL_DIR / "random_forest_polda.pkl"
    features_path = settings.MODEL_DIR / "model_features.pkl"
    
    if model_path.exists() and features_path.exists():
        model = joblib.load(model_path)
        features = joblib.load(features_path)
        return model, features
    else:
        return None, None

# Load Assets
df, data_source = load_data()
model, model_features = load_ml_model()

# ==============================================================================
# UI INTERFACE STREAMLIT
# ==============================================================================
st.title("🔮 Simulator Prediksi Keselamatan Jalan Polda Jateng")
st.markdown("Aplikasi simulator Machine Learning untuk memprediksi fatalitas kecelakaan jalan raya di Jawa Tengah.")

if df is not None:
    # Display configuration status in the sidebar
    st.sidebar.title("Status Konfigurasi")
    st.sidebar.info(f"📁 **Sumber Kalibrasi:** {data_source}")
    if model is not None:
        st.sidebar.success("🤖 **Status Model ML:** Aktif & Siap pakai")
    else:
        st.sidebar.warning("⚠️ **Status Model ML:** Model belum ditraining. Jalankan 'python main.py' untuk melatih model.")

    if model is not None:
        st.markdown("### ⚙️ Parameter Masukan Wilayah")
        st.markdown("Geser parameter di bawah ini untuk melihat perkiraan dampak volume kendaraan, infrastruktur jalan, dan cuaca terhadap tingkat fatalitas kecelakaan (korban meninggal per tahun).")
        
        col_in1, col_in2, col_in3 = st.columns(3)
        
        with col_in1:
            st.markdown("### 🚗 Volume Kendaraan")
            motor = st.slider("Jumlah Sepeda Motor", int(df['sepeda_motor'].min()), int(df['sepeda_motor'].max()), int(df['sepeda_motor'].median()))
            truk = st.slider("Jumlah Truk", int(df['truk'].min()), int(df['truk'].max()), int(df['truk'].median()))
            mobil = st.slider("Jumlah Mobil Penumpang", int(df['mobil_penumpang'].min()), int(df['mobil_penumpang'].max()), int(df['mobil_penumpang'].median()))
            bus = st.slider("Jumlah Bus", int(df['bus'].min()), int(df['bus'].max()), int(df['bus'].median()))
            
        with col_in2:
            st.markdown("### 🛣️ Infrastruktur Jalan (KM)")
            j_baik = st.slider("Jalan Kondisi Baik", int(df['jalan_kondisi_baik'].min()), int(df['jalan_kondisi_baik'].max()), int(df['jalan_kondisi_baik'].median()))
            j_sedang = st.slider("Jalan Kondisi Sedang", int(df['jalan_kondisi_sedang'].min()), int(df['jalan_kondisi_sedang'].max()), int(df['jalan_kondisi_sedang'].median()))
            j_rusak = st.slider("Jalan Kondisi Rusak", int(df['jalan_kondisi_rusak'].min()), int(df['jalan_kondisi_rusak'].max()), int(df['jalan_kondisi_rusak'].median()))
            j_rb = st.slider("Jalan Rusak Berat", int(df['jalan_kondisi_rusak_berat'].min()), int(df['jalan_kondisi_rusak_berat'].max()), int(df['jalan_kondisi_rusak_berat'].median()))
            
        with col_in3:
            st.markdown("### 🌤️ Faktor Alam & Cuaca")
            suhu = st.slider("Rata-rata Suhu (°C)", float(df['suhu_avg'].min()), float(df['suhu_avg'].max()), float(df['suhu_avg'].median()))
            lembab = st.slider("Rata-rata Kelembaban (%)", float(df['kelembaban_avg'].min()), float(df['kelembaban_avg'].max()), float(df['kelembaban_avg'].median()))
            curah = st.slider("Curah Hujan (mm)", float(df['curah_hujan'].min()), float(df['curah_hujan'].max()), float(df['curah_hujan'].median()))
            hari_h = st.slider("Jumlah Hari Hujan", int(df['hari_hujan'].min()), int(df['hari_hujan'].max()), int(df['hari_hujan'].median()))

        # Model inputs matching exact training features
        input_data = pd.DataFrame([{
            'mobil_penumpang': mobil,
            'bus': bus,
            'truk': truk,
            'sepeda_motor': motor,
            'jalan_kondisi_baik': j_baik,
            'jalan_kondisi_sedang': j_sedang,
            'jalan_kondisi_rusak': j_rusak,
            'jalan_kondisi_rusak_berat': j_rb,
            'suhu_avg': suhu,
            'kelembaban_avg': lembab,
            'curah_hujan': curah,
            'hari_hujan': hari_h
        }])
        
        st.markdown("---")
        
        # Predict Button
        if st.button("🚀 Hitung Estimasi Fatalitas Risiko Wilayah", use_container_width=True):
            prediksi = model.predict(input_data)[0]
            
            st.subheader("🔮 Hasil Estimasi Prediksi:")
            st.error(f"## **{int(np.round(prediksi))} Korban Meninggal Dunia** per tahun di bawah kondisi variabel ini.")
            st.caption("Prediksi dihasilkan secara otomatis oleh model Machine Learning Random Forest Regressor yang dilatih menggunakan data gabungan Polda Jateng & BMKG.")
    else:
        st.warning("⚠️ Simulator tidak dapat dijalankan karena model machine learning belum tersedia. Silakan jalankan training terlebih dahulu.")
else:
    st.error("Gagal memuat dashboard. Periksa kembali log pipeline Anda.")
