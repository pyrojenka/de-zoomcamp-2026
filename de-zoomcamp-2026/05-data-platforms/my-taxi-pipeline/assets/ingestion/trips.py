"""@bruin
name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default

materialization:
  type: table
  strategy: append

columns:
  - name: pickup_datetime
    type: timestamp
  - name: dropoff_datetime
    type: timestamp
  - name: pickup_location_id
    type: integer
  - name: dropoff_location_id
    type: integer
  - name: fare_amount
    type: float
  - name: payment_type
    type: integer
  - name: taxi_type
    type: string
@bruin"""

import os
import json
import pandas as pd
import requests
import io
from datetime import datetime
from dateutil.relativedelta import relativedelta

def materialize():
    # 1. Get environment variables
    start_date_str = os.environ.get("BRUIN_START_DATE")
    end_date_str = os.environ.get("BRUIN_END_DATE")
    vars_env = os.environ.get("BRUIN_VARS", "{}")
    taxi_types = json.loads(vars_env).get("taxi_types", ["yellow"])

    if not start_date_str or not end_date_str:
        print("Start or end date not provided. Skipping.")
        return pd.DataFrame()

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    all_dfs = []
    
    # 2. Iterate through each month in the range
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        year = current_date.year
        month = f"{current_date.month:02d}"
        
        for taxi_type in taxi_types:
            url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year}-{month}.parquet"
            print(f"Fetching data from {url}...")
            
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 404:
                    print(f"File not found: {url}")
                    continue
                response.raise_for_status()
                
                df = pd.read_parquet(io.BytesIO(response.content))
                
                # Normalize column names to lowercase
                df.columns = [c.lower() for c in df.columns]
                
                # Handling pickup/dropoff column names
                if taxi_type == "yellow":
                    df = df.rename(columns={
                        "tpep_pickup_datetime": "pickup_datetime",
                        "tpep_dropoff_datetime": "dropoff_datetime"
                    })
                elif taxi_type == "green":
                    df = df.rename(columns={
                        "lpep_pickup_datetime": "pickup_datetime",
                        "lpep_dropoff_datetime": "dropoff_datetime"
                    })
                
                # Standardize common column names to match trips.sql expectations
                rename_map = {
                    "pulocationid": "pickup_location_id",
                    "dolocationid": "dropoff_location_id",
                    "payment_type": "payment_type",
                    "fare_amount": "fare_amount"
                }
                df = df.rename(columns=rename_map)
                
                # Add metadata
                df['taxi_type'] = taxi_type
                
                # Filter by actual date range requested
                mask = (df['pickup_datetime'] >= start_date) & (df['pickup_datetime'] <= end_date)
                df = df.loc[mask]

                if not df.empty:
                    all_dfs.append(df)
                    print(f"Loaded {len(df)} rows for {taxi_type} {year}-{month}")
                    
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                continue
        
        current_date += relativedelta(months=1)

    # 3. Combine results
    if not all_dfs:
        print("No data found for the specified period.")
        return pd.DataFrame()

    final_df = pd.concat(all_dfs, ignore_index=True)
    
    # Required columns for trips.sql
    requested_columns = [
        "pickup_datetime", 
        "dropoff_datetime", 
        "pickup_location_id", 
        "dropoff_location_id", 
        "fare_amount", 
        "payment_type", 
        "taxi_type"
    ]
    
    for col in requested_columns:
        if col not in final_df.columns:
            final_df[col] = None
            
    return final_df[requested_columns]
