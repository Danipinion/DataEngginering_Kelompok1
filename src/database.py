import pandas as pd
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_engine(db_uri: str):
    """Creates a database engine for the given connection URI."""
    try:
        engine = create_engine(db_uri)
        logging.info("Database engine successfully configured.")
        return engine
    except Exception as e:
        logging.error(f"Failed to configure database engine: {e}")
        raise e

def upload_to_db(df: pd.DataFrame, table_name: str, db_uri: str) -> None:
    """Uploads the dataframe to the database table."""
    try:
        engine = get_engine(db_uri)
        logging.info(f"Uploading data to table '{table_name}' in the database...")
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=1000
        )
        logging.info("Upload complete!")
    except Exception as e:
        logging.error(f"Error during upload: {e}")
        raise e

def fetch_from_db(table_name: str, db_uri: str) -> pd.DataFrame:
    """Fetches the data from the database table."""
    try:
        engine = get_engine(db_uri)
        logging.info(f"Fetching data from table '{table_name}'...")
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", con=engine)
        logging.info(f"Successfully fetched {df.shape[0]} rows and {df.shape[1]} columns.")
        return df
    except Exception as e:
        logging.error(f"Error during fetch: {e}")
        raise e
