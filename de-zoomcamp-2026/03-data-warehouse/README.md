# Data Engineering Zoomcamp 2026 - Homework 3: Data Warehouse

This homework focuses on working with BigQuery and Google Cloud Storage using Yellow Taxi Trip Records for January 2024 - June 2024.

## Setup Instructions

### 1. Load Data to GCS

Run the provided Python script to load data into your GCS bucket:

```bash
python load_yellow_taxi_data.py
```

*Note: Ensure you have a Service Account with GCS Admin privileges or are authenticated via Google SDK.*

### 2. Create BigQuery Tables

**Create External Table:**

```sql
CREATE OR REPLACE EXTERNAL TABLE `taxi-rides-ny.nytaxi.external_yellow_tripdata`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://your-bucket-name/yellow_tripdata_2024-*.parquet']
);
```

**Create Regular (Materialized) Table:**

```sql
CREATE OR REPLACE TABLE `taxi-rides-ny.nytaxi.native_yellow_tripdata` AS
SELECT * FROM `taxi-rides-ny.nytaxi.external_yellow_tripdata`;
```

## Questions and Queries

### Question 1: Counting records

**Query:**
```sql
SELECT count(*) FROM `taxi-rides-ny.nytaxi.native_yellow_tripdata`;
```

**Answer:** 20,332,093

### Question 2: Data read estimation (External vs Materialized)

**Query:**
```sql
SELECT COUNT(DISTINCT(PULocationID)) FROM `taxi-rides-ny.nytaxi.external_yellow_tripdata`;
SELECT COUNT(DISTINCT(PULocationID)) FROM `taxi-rides-ny.nytaxi.native_yellow_tripdata`;
```

**Answer:** 0 MB for the External Table and 155.12 MB for the Materialized Table

### Question 3: Understanding columnar storage

**Queries:**
```sql
-- Query 1
SELECT PULocationID FROM `taxi-rides-ny.nytaxi.native_yellow_tripdata`;

-- Query 2
SELECT PULocationID, DOLocationID FROM `taxi-rides-ny.nytaxi.native_yellow_tripdata`;
```

**Answer:** BigQuery is a columnar database. Querying two columns requires reading more data than querying one.

### Question 4: Counting zero fare trips

**Query:**
```sql
SELECT count(*) FROM `taxi-rides-ny.nytaxi.native_yellow_tripdata` WHERE fare_amount = 0;
```

**Answer:** 8,333

### Question 5: Partitioning and clustering strategy

**Best Strategy:** Partition by `tpep_dropoff_datetime` and Cluster on `VendorID`.

**Creating Query:**
```sql
CREATE OR REPLACE TABLE `taxi-rides-ny.nytaxi.yellow_tripdata_partitioned_clustered`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS
SELECT * FROM `taxi-rides-ny.nytaxi.external_yellow_tripdata`;
```

### Question 6: Partition benefits

**Query:**
```sql
SELECT DISTINCT VendorID
FROM `taxi-rides-ny.nytaxi.native_yellow_tripdata`
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15';

SELECT DISTINCT VendorID
FROM `taxi-rides-ny.nytaxi.yellow_tripdata_partitioned_clustered`
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15';
```

**Answer:** 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table

### Question 7: External table storage

**Answer:** GCP Bucket

### Question 8: Clustering best practices

**Answer:** False (Clustering is not always best practice, depending on data size and query patterns).

### Question 9: Understanding table scans

**Query:**
```sql
SELECT count(*) FROM `taxi-rides-ny.nytaxi.native_yellow_tripdata`;
```

**Answer:** 0 Bytes. This is because `COUNT(*)` on a non-external table retrieves metadata statistics without scanning the actual data.
