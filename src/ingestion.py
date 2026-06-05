import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_kecelakaan(file_path: str) -> pd.DataFrame:
    """Loads and performs initial cleaning of the Accident data."""
    logging.info(f"Loading accident data from: {file_path}")
    df = pd.read_csv(file_path, skiprows=4, header=None)
    df.columns = ['Kabupaten_Kota', 'Meninggal', 'Luka_Berat', 'Luka_Ringan']
    
    # Remove number prefix (e.g., '1. Cilacap' -> 'Cilacap')
    df['Kabupaten_Kota'] = df['Kabupaten_Kota'].str.replace(r'^\d+\s+', '', regex=True).str.strip()
    
    # Remove total row (usually the first row)
    df = df.iloc[1:].reset_index(drop=True)
    
    # Convert data types
    df['Kabupaten_Kota'] = df['Kabupaten_Kota'].astype('string')
    for col in ['Meninggal', 'Luka_Berat', 'Luka_Ringan']:
        df[col] = df[col].astype('float')
        
    return df

def load_kendaraan(file_path: str) -> pd.DataFrame:
    """Loads and performs initial cleaning of the Vehicles data."""
    logging.info(f"Loading vehicle data from: {file_path}")
    df = pd.read_csv(file_path)
    df.columns = ['Kabupaten_Kota', 'Mobil_Penumpang', 'Bus', 'Truk', 'Sepeda_Motor', 'Jumlah']
    
    # Skip header-like rows or total provincial row
    df = df.iloc[3:].reset_index(drop=True)
    df = df[~df['Kabupaten_Kota'].str.contains('PROVINSI', na=False)]
    
    # Clean city names and convert data types
    df['Kabupaten_Kota'] = df['Kabupaten_Kota'].str.replace(r'^\d+\s+', '', regex=True).str.strip()
    df['Kabupaten_Kota'] = df['Kabupaten_Kota'].astype('string')
    
    numeric_cols = ['Mobil_Penumpang', 'Bus', 'Truk', 'Sepeda_Motor', 'Jumlah']
    for col in numeric_cols:
        df[col] = df[col].astype('float')
        
    return df

def load_jalan(file_path: str) -> pd.DataFrame:
    """Loads and performs initial cleaning of the Road Condition data."""
    logging.info(f"Loading road condition data from: {file_path}")
    df = pd.read_csv(file_path, skiprows=5, header=None)
    df.columns = ['No', 'Kabupaten_Kota', 'Baik', 'Sedang', 'Rusak', 'Rusak_Berat']
    df = df.drop(columns=['No'])
    
    # Drop rows where Kabupaten_Kota is NaN
    df = df.dropna(subset=['Kabupaten_Kota'])
    
    # Basic filter for empty/invalid city names
    df['Kabupaten_Kota'] = df['Kabupaten_Kota'].astype(str).str.strip()
    df = df[~df['Kabupaten_Kota'].isin(['0', 'nan', '', '0.0'])]
    df = df.reset_index(drop=True)
    
    df['Kabupaten_Kota'] = df['Kabupaten_Kota'].astype('string')
    
    # Clean string format and cast to float
    for col in ['Baik', 'Sedang', 'Rusak']:
        df[col] = df[col].astype(str).str.replace(' ', '', regex=False).astype('float')
        
    df['Rusak_Berat'] = pd.to_numeric(df['Rusak_Berat'].astype(str).str.replace(' ', '', regex=False), errors='coerce')
    df = df.fillna(0.0)
    
    return df

def load_cuaca(file_path: str) -> pd.DataFrame:
    """Loads and performs initial cleaning of the Weather data."""
    logging.info(f"Loading weather data from: {file_path}")
    df = pd.read_csv(file_path, skiprows=5, header=None)
    df = df.dropna(how='all')
    df.columns = [
        'No', 'Kabupaten_Kota', 'Stasiun_BMKG',
        'Suhu_Min', 'Suhu_Avg', 'Suhu_Max',
        'Kelembaban_Min', 'Kelembaban_Avg', 'Kelembaban_Max',
        'Angin_Min', 'Angin_Avg', 'Angin_Max',
        'Tekanan_Min', 'Tekanan_Avg', 'Tekanan_Max',
        'Curah_Hujan', 'Hari_Hujan', 'Penyinaran_Matahari'
    ]
    df = df.drop(columns=['No'])
    df = df.replace(r'^\s*-\s*$', np.nan, regex=True)
    
    return df
