import pandas as pd
import numpy as np
import joblib
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def train_model(
    df: pd.DataFrame, 
    features: list[str], 
    target: str,
    random_state: int = 42
) -> tuple[RandomForestRegressor, dict[str, float], pd.DataFrame, pd.Series]:
    """
    Splits the data into train/test sets, trains a RandomForestRegressor,
    and evaluates it using MAE and R2.
    """
    logging.info("Preparing data for training...")
    X = df[features]
    y = df[target]

    # Split data (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )

    logging.info("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=random_state)
    model.fit(X_train, y_train)

    # Evaluate Model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    metrics = {"mae": mae, "r2": r2}
    logging.info(f"Model Training Complete. MAE: {metrics['mae']:.2f} | R2 Score: {metrics['r2']:.2f}")

    return model, metrics, X_test, y_test

def save_model_artifacts(
    model: RandomForestRegressor, 
    features: list[str], 
    model_dir: Path,
    model_name: str = "random_forest_polda.pkl",
    features_name: str = "model_features.pkl"
) -> None:
    """Saves the trained model and feature list as pickle files."""
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = model_dir / model_name
    features_path = model_dir / features_name
    
    logging.info(f"Saving model to: {model_path}")
    joblib.dump(model, model_path)
    
    logging.info(f"Saving features to: {features_path}")
    joblib.dump(features, features_path)
    
    logging.info("Model artifacts saved successfully.")
