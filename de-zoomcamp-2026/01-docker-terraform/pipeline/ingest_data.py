import pandas as pd
from sqlalchemy import create_engine, text
import time
import click
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
TAXI_DATA_BASE_URL = 'https://d37ci6vzurychx.cloudfront.net/trip-data/'
ZONES_URL = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv'
ZONES_TABLE = 'zone_lookup'

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--year', default=2025, type=int, help='Year of the data')
@click.option('--month', default=11, type=int, help='Month of the data')
@click.option('--target-table', default='green_taxi_data', help='Target table name')
def ingest_data(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, target_table):
    """
    Ingest taxi data and zone lookup data into PostgreSQL database.
    
    Downloads green taxi data for the specified year and month, and zone lookup data,
    then loads them into the database.
    """
    
    # Use environment variables if not provided
    pg_user = os.getenv('PG_USER', pg_user)
    pg_pass = os.getenv('PG_PASS', pg_pass)
    pg_host = os.getenv('PG_HOST', pg_host)
    pg_port = int(os.getenv('PG_PORT', pg_port))
    pg_db = os.getenv('PG_DB', pg_db)
    
    # 1. Form the URL dynamically (add 0 before the month if it's < 10)
    taxi_url = f'{TAXI_DATA_BASE_URL}green_tripdata_{year}-{month:02d}.parquet'
    
    # 2. Create connection
    connection_string = f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    engine = create_engine(connection_string)
    
    # 3. Loading taxi data
    logger.info(f"Connecting to database at {pg_host}...")
    logger.info(f"Downloading taxi data for {year}-{month:02d}...")
    
    try:
        t_start = time.time()
        df = pd.read_parquet(taxi_url)
        
        # Write to database (replace deletes the old table if it existed)
        df.to_sql(name=target_table, con=engine, if_exists='replace', chunksize=10000, index=False)
        
        t_end = time.time()
        logger.info(f"Success! {len(df)} rows loaded into '{target_table}' in {t_end - t_start:.2f}s")
        
    except Exception as e:
        logger.error(f"Error during taxi ingestion: {e}")
        return  # Exit on error

    # 4. Loading zones (only if not exists)
    logger.info("Checking zone lookup data...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{ZONES_TABLE}')"))
            table_exists = result.fetchone()[0]
        
        if not table_exists:
            logger.info("Downloading zone lookup data...")
            df_z = pd.read_csv(ZONES_URL)
            df_z.to_sql(name=ZONES_TABLE, con=engine, if_exists='replace', index=False)
            logger.info(f"Success! {len(df_z)} zones loaded into '{ZONES_TABLE}'")
        else:
            logger.info(f"Zone lookup table '{ZONES_TABLE}' already exists, skipping...")
            
    except Exception as e:
        logger.error(f"Error during zone ingestion: {e}")

if __name__ == '__main__':
    ingest_data()