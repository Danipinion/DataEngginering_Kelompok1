#!/bin/bash
# Menghentikan script jika terjadi error
set -e

echo "===================================================="
echo "🔮 MEMULAI PENGECEKAN MODEL MACHINE LEARNING..."
echo "===================================================="

# Cek apakah file model dan fitur telah tersedia
if [ ! -f "models/random_forest_polda.pkl" ] || [ ! -f "models/model_features.pkl" ]; then
    echo "⚠️ Model ML tidak ditemukan di folder host 'models/'."
    echo "🚀 Menjalankan pipeline training otomatis..."
    
    # Jalankan training (menggunakan local-only jika database offline, atau otomatis load database jika online)
    python main.py
    
    echo "✅ Training model otomatis selesai!"
else
    echo "🤖 Model ML ditemukan. Melewati langkah training otomatis."
fi

echo "===================================================="
echo "🚀 MENJALANKAN SERVICE STREAMLIT..."
echo "===================================================="
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0
