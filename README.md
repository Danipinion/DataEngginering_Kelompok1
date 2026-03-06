
## Project Information

**Project Name**: Analisis Prediktif Tingkat Kecelakaan Lalu Lintas di Jawa Tengah
**Created By**: Data Engineering Kelompok 1
**Date**: February 10, 2026
**Version**: 1.0

## 1. Executive Summary

### 1.1 Project Overview

- **Tujuan Project**: Mengembangkan sistem analitik untuk prediksi tingkat kecelakaan lalu lintas di Jawa Tengah menggunakan berbagai sumber open data
- **Scope Project**: Integrasi data real-time dari API cuaca, titik rawan kecelakaan (blackspot), dan volume kendaraan di jalur utama Jawa Tengah.
- **Expected Outcomes**: Dashboard pemetaan risiko kecelakaan prediktif
- **Timeline**: 4 bulan (Februari - Juni 2026)

### 1.2 Stakeholders

- **Project Owner**: Kelompok 1
- **Team Members**:
  - Data Engineer: Mohammad Dani Taufiqurrohman
  - Data Analyst: Novandy Triarto W.
  - Project Manager: Habib Hajid Taqiuddin
- **End Users**:
  - Dinas Perhubungan
  - Operator Transportasi
  - Masyarakat umum

## 2. Data Source Analysis

### 2.1 Data Kendaraan Bermotor

#### Source Details

- **Dataset Name**: Jumlah Kendaraan Bermotor Menurut Kabupaten/Kota dan Jenis Kendaraan di Provinsi Jawa Tengah (Unit)
- **URL/Access Point**: https://jateng.bps.go.id/id/statistics-table/2/MTAwNiMy/jumlah-kendaraan-bermotor-menurut-kabupaten-kota-dan-jenis-kendaraan-di-provinsi-jawa-tengah
- **Data Owner**: Badan Pusat Statistik Provinsi Jawa Tengah
- **Last Update**: 10 Maret 2022

#### Data Analysis

- **Format Data**: CSV
- **Volume Data**: 2,173KB
- **Time Coverage**: Januari 2024 - Desember 2024
- **Data Quality**:
  - Metadata jelas, kategori kendaraan mengikuti standar Samsat.

### 2.2 Data Kecelakaan Lalu Lintas

#### Source Details

- **Dataset Name**: Jumlah Korban Kecelakaan Lalu Lintas di Wilayah Polda Jawa Tengah Tahun (Jiwa)
- **URL/Access Point**: https://jateng.bps.go.id/id/statistics-table/2/NTYzIzI=/jumlah-korban-kecelakaan-lalu-lintas-di-wilayah-polda-jawa-tengah-tahun.html
- **Creator/Publisher**: Badan Pusat Statistik Provinsi Jawa Tengah
- **Last Update**: 8 April 2021

#### Data Analysis

- **Format Data**: CSV
- **Volume Data**: 1,32KB
- **Data Fields**:
  - Kabupate / Kota
  - Meninggal
  - Luka Berat
  - Luka Ringan
- **Quality Metrics**:
  - Completeness: Tinggi
  - Accuracy: High
  - Consistency: Sangat baik

### 2.3 Data Infrastruktur Jalan (BPS Jateng)

#### Source Details

- **Dataset Name**: Panjang Jalan Menurut Kab/Kota dan Kondisi Jalan (km)
- **Endpoint URL**: (https://jateng.bps.go.id/id/statistics-table/1/MjQ1NSMx/panjang-jalan-menurut-kabupaten-kota-dan-kondisi-jalan--di-provinsi-jawa-tengah--km---2020.html)
- **Provider**: BPS Provinsi Jawa Tengah

#### Data Analysis

- **Format & Structure**: Tabular (CSV/Excel)
- **Data Volume**: Small
- **Data Fields**: Kondisi Jalan (Baik, Sedang, Rusak, Rusak Berat)
- **Quality Metrics**: Crucial untuk korelasi kecelakaan akibat faktor infrastruktur fisik

### 2.4 Data Cuaca & Lingkungan (Google Earth Engine - GEE)

#### Source Details

- **Dataset Name**: ERA5-Land Monthly Averaged / CHIRPS Daily
- **Provider**: ECMWF / UC Santa Barbara (via GEE API)
- **Authentication Method**: Service Account / OAuth2
