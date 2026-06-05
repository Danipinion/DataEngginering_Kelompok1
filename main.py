import argparse
import sys
import logging
from config import settings
from src.ingestion import load_kecelakaan, load_kendaraan, load_jalan, load_cuaca
from src.preprocessing import preprocess_and_merge, clean_final_data
from src.database import upload_to_db, fetch_from_db
from src.training import train_model, save_model_artifacts

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_pipeline(skip_db_upload: bool = False, use_db_for_train: bool = True):
    """Runs the end-to-end data engineering and machine learning pipeline."""
    logging.info("=== STARTING PIPELINE ===")

    # 1. DATA INGESTION
    logging.info("--- Phase 1: Data Ingestion ---")
    try:
        kecelakaan_df = load_kecelakaan(settings.RAW_DATA_DIR / settings.FILE_KECELAKAAN)
        kendaraan_df = load_kendaraan(settings.RAW_DATA_DIR / settings.FILE_KENDARAAN)
        jalan_df = load_jalan(settings.RAW_DATA_DIR / settings.FILE_JALAN)
        cuaca_df = load_cuaca(settings.RAW_DATA_DIR / settings.FILE_CUACA)
    except FileNotFoundError as e:
        logging.error(
            f"Raw data file not found: {e}. Please ensure raw CSV files are placed in: {settings.RAW_DATA_DIR}"
        )
        sys.exit(1)

    # 2. PREPROCESSING & MERGING
    logging.info("--- Phase 2: Preprocessing & Merging ---")
    df_merged = preprocess_and_merge(kecelakaan_df, kendaraan_df, jalan_df, cuaca_df)
    df_cleaned, medians = clean_final_data(df_merged)

    # Save processed locally as a backup / check
    processed_csv_path = settings.PROCESSED_DATA_DIR / "data_polda_jateng_cleaned.csv"
    df_cleaned.to_csv(processed_csv_path, index=False)
    logging.info(f"Local cleaned file saved to: {processed_csv_path}")

    # 3. DATABASE UPLOAD
    if not skip_db_upload:
        logging.info("--- Phase 3: Database Upload (Aiven) ---")
        try:
            upload_to_db(df_cleaned, settings.TABLE_NAME, settings.AIVEN_DATABASE_URI)
        except Exception as e:
            logging.error(f"Failed to upload to DB. Continuing local process. Error: {e}")

    # 4. TRAINING & EVALUATION
    logging.info("--- Phase 4: Model Training & Evaluation ---")
    training_df = df_cleaned
    if use_db_for_train and not skip_db_upload:
        try:
            training_df = fetch_from_db(settings.TABLE_NAME, settings.AIVEN_DATABASE_URI)
        except Exception as e:
            logging.warning(f"Could not fetch from database. Falling back to local data. Error: {e}")

    model, metrics, X_test, y_test = train_model(
        df=training_df,
        features=settings.FEATURES,
        target=settings.TARGET
    )

    # 5. ARTIFACT SAVING
    logging.info("--- Phase 5: Saving Model Artifacts ---")
    save_model_artifacts(
        model=model,
        features=settings.FEATURES,
        model_dir=settings.MODEL_DIR
    )
    
    logging.info("=== PIPELINE RUN SUCCESSFUL ===")
    print("\n--- Model Metrics Summary ---")
    print(f"MAE (Mean Absolute Error): {metrics['mae']:.2f}")
    print(f"R2 Score: {metrics['r2']:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Polda Jateng ML Pipeline")
    parser.add_argument("--skip-upload", action="store_true", help="Skip uploading cleaned data to database")
    parser.add_argument("--local-only", action="store_true", help="Run local pipeline without database interactions")
    
    args = parser.parse_args()
    
    skip_upload = args.skip_upload or args.local_only
    use_db = not args.local_only

    run_pipeline(skip_db_upload=skip_upload, use_db_for_train=use_db)
