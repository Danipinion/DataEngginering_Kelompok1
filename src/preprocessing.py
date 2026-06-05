import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def preprocess_and_merge(
    kecelakaan_df: pd.DataFrame, 
    kendaraan_df: pd.DataFrame, 
    jalan_df: pd.DataFrame, 
    cuaca_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merges all four dataframes (kecelakaan, kendaraan, jalan, cuaca) and performs the
    necessary cleanings, alignments, and aggregations.
    """
    logging.info("Starting preprocessing and merging pipeline...")
    
    # 1. Align Kabupaten_Kota for jalan_df using kecelakaan_df values (if they have the same size)
    if len(jalan_df) == len(kecelakaan_df):
        logging.info("Aligning jalan_df city names with kecelakaan_df")
        jalan_df['Kabupaten_Kota'] = kecelakaan_df['Kabupaten_Kota'].values
    else:
        logging.warning("Lengths of jalan_df and kecelakaan_df do not match. Skipping direct alignment.")
    
    # 2. Initial merge of accident, vehicle, and road data
    df_gabungan = pd.merge(kecelakaan_df, kendaraan_df, on='Kabupaten_Kota', how='outer')
    df_gabungan = pd.merge(df_gabungan, jalan_df, on='Kabupaten_Kota', how='outer')
    
    # 3. Weather data preprocessing
    cuaca_df['Kabupaten_Kota'] = cuaca_df['Kabupaten_Kota'].ffill().str.strip()
    
    # Differentiate Kabupaten and Kota based on original index logic (index >= 33 is Kota)
    is_kota = cuaca_df.index >= 33
    cuaca_df.loc[~is_kota, 'Kabupaten_Kota'] = 'Kabupaten ' + cuaca_df.loc[~is_kota, 'Kabupaten_Kota']
    cuaca_df.loc[is_kota, 'Kabupaten_Kota'] = 'Kota ' + cuaca_df.loc[is_kota, 'Kabupaten_Kota']
    
    # Standardize name for matching
    cuaca_df['Kabupaten_Kota'] = cuaca_df['Kabupaten_Kota'].str.replace(r'^(Kabupaten|Kota)\s+', '', regex=True).str.strip()
    
    kolom_cuaca = [
        'Suhu_Min', 'Suhu_Avg', 'Suhu_Max',
        'Kelembaban_Min', 'Kelembaban_Avg', 'Kelembaban_Max',
        'Angin_Min', 'Angin_Avg', 'Angin_Max',
        'Tekanan_Min', 'Tekanan_Avg', 'Tekanan_Max',
        'Curah_Hujan', 'Hari_Hujan', 'Penyinaran_Matahari'
    ]
    
    for col in kolom_cuaca:
        cuaca_df[col] = pd.to_numeric(cuaca_df[col].astype(str).str.replace(' ', '', regex=False), errors='coerce')
        
    cuaca_numeric = cuaca_df.drop(columns=['Stasiun_BMKG'], errors='ignore')
    cuaca_clean = cuaca_numeric.groupby('Kabupaten_Kota').mean().reset_index()
    
    # 4. Final merging using clean matching keys
    df_gabungan['Kunci_Cocok'] = df_gabungan['Kabupaten_Kota'].str.replace('Kabupaten ', '', case=False).str.replace('Kota ', '', case=False).str.strip().str.lower()
    cuaca_clean['Kunci_Cocok'] = cuaca_clean['Kabupaten_Kota'].str.replace('Kabupaten ', '', case=False).str.replace('Kota ', '', case=False).str.strip().str.lower()
    
    df_merged = pd.merge(df_gabungan, cuaca_clean.drop(columns=['Kabupaten_Kota']), on='Kunci_Cocok', how='left')
    df_merged = df_merged.drop(columns=['Kunci_Cocok'])
    
    return df_merged

def clean_final_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    """
    Standardizes schema, casts target types, drops unnecessary columns, and handles
    missing values by imputing with median.
    """
    logging.info("Cleaning merged dataset and imputing missing values...")
    
    # Standardize column names to lowercase snake_case
    new_names = {
        'Kabupaten_Kota': 'kabupaten_kota',
        'Meninggal': 'korban_meninggal',
        'Luka_Berat': 'korban_luka_berat',
        'Luka_Ringan': 'korban_luka_ringan',
        'Mobil_Penumpang': 'mobil_penumpang',
        'Bus': 'bus',
        'Truk': 'truk',
        'Sepeda_Motor': 'sepeda_motor',
        'Jumlah': 'jumlah_kendaraan',
        'Baik': 'jalan_kondisi_baik',
        'Sedang': 'jalan_kondisi_sedang',
        'Rusak': 'jalan_kondisi_rusak',
        'Rusak_Berat': 'jalan_kondisi_rusak_berat',
        'Suhu_Min': 'suhu_min',
        'Suhu_Avg': 'suhu_avg',
        'Suhu_Max': 'suhu_max',
        'Kelembaban_Min': 'kelembaban_min',
        'Kelembaban_Avg': 'kelembaban_avg',
        'Kelembaban_Max': 'kelembaban_max',
        'Angin_Min': 'angin_min',
        'Angin_Avg': 'angin_avg',
        'Angin_Max': 'angin_max',
        'Tekanan_Min': 'tekanan_min',
        'Tekanan_Avg': 'tekanan_avg',
        'Tekanan_Max': 'tekanan_max',
        'Curah_Hujan': 'curah_hujan',
        'Hari_Hujan': 'hari_hujan',
        'Penyinaran_Matahari': 'penyinaran_matahari'
    }
    df_cleaned = df.rename(columns=new_names)

    # Drop columns that are completely empty
    if 'angin_min' in df_cleaned.columns:
        df_cleaned = df_cleaned.drop(columns=['angin_min'])

    # Convert count columns to integer
    int_cols = [
        'korban_meninggal', 'korban_luka_berat', 'korban_luka_ringan',
        'mobil_penumpang', 'bus', 'truk', 'sepeda_motor', 'jumlah_kendaraan',
        'jalan_kondisi_baik', 'jalan_kondisi_sedang', 'jalan_kondisi_rusak', 'jalan_kondisi_rusak_berat'
    ]
    for col in int_cols:
        if col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].fillna(0).astype('int64')

    # Handle missing values for weather columns using median
    weather_cols = [
        'suhu_min', 'suhu_avg', 'suhu_max', 'kelembaban_min', 'kelembaban_avg',
        'kelembaban_max', 'angin_avg', 'angin_max', 'tekanan_min', 'tekanan_avg',
        'tekanan_max', 'curah_hujan', 'hari_hujan', 'penyinaran_matahari'
    ]

    medians = {}
    for col in weather_cols:
        if col in df_cleaned.columns:
            median_val = df_cleaned[col].median()
            df_cleaned[col] = df_cleaned[col].fillna(median_val)
            medians[col] = median_val

    return df_cleaned, medians
