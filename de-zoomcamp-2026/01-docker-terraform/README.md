# Data Engineering Zoomcamp 2026 - Homework 1: Docker & Terraform

This homework focuses on setting up a data pipeline using Docker and Terraform to ingest NYC taxi data into PostgreSQL and perform SQL analysis.

## Prerequisites

- Docker and Docker Compose installed
- Terraform installed (if using Terraform for infrastructure)
- Python 3.8+ (for the ingestion script)

## Project Structure

```
01-docker-terraform/
├── README.md
└── pipeline/
    ├── docker-compose.yaml
    ├── Dockerfile
    ├── ingest_data.py
    └── pyproject.toml
```

## Setup Instructions

### 1. Start PostgreSQL Database with pgAdmin

Navigate to the pipeline directory and start the services:

```bash
cd pipeline
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- pgAdmin on port 8085

Access pgAdmin at http://localhost:8085 with:
- Email: admin@admin.com
- Password: root

### 2. Build the Data Ingestion Image

```bash
docker build -t taxi_ingest:v001 .
```

### 3. Run Data Ingestion

```bash
docker run -it \
  --network=pipeline_default \
  taxi_ingest:v001 \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=pgdatabase \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --year=2025 \
  --month=11 \
  --target-table=green_taxi_data
```

This will:
- Download green taxi data for November 2025
- Load it into the `green_taxi_data` table
- Download and load zone lookup data into `zone_lookup` table

## SQL Questions

After ingesting the data, answer the following questions using pgAdmin or any SQL client:

### Question 3: Counting short trips
How many trips in November 2025 had a trip distance of less than or equal to 1 mile?

```sql
SELECT
    COUNT(1)
FROM
    green_taxi_data
WHERE
    lpep_pickup_datetime >= '2025-11-01'
    AND lpep_pickup_datetime < '2025-12-01'
    AND trip_distance <= 1.0;
```

### Question 4: Longest trip for each day
Which was the pick-up day with the longest trip distance? (Considering trips < 100 miles).

```sql
SELECT
    lpep_pickup_datetime::DATE AS pickup_day,
    MAX(trip_distance) AS max_distance
FROM
    green_taxi_data
WHERE
    trip_distance < 100
GROUP BY
    pickup_day
ORDER BY
    max_distance DESC
LIMIT 1;
```

### Question 5: Biggest pickup zone
Which was the pickup zone with the largest total_amount (sum of all trips) on November 18th, 2025?

```sql
SELECT
    z."Zone" AS pickup_zone,
    SUM(t.total_amount) AS total_amount_sum
FROM
    green_taxi_data t
JOIN
    zone_lookup z ON t."PULocationID" = z."LocationID"
WHERE
    t.lpep_pickup_datetime::DATE = '2025-11-18'
GROUP BY
    1
ORDER BY
    2 DESC
LIMIT 1;
```

### Question 6: Largest tip
For passengers picked up in "East Harlem North" in November 2025, which drop-off zone had the largest tip?

```sql
SELECT
    do_z."Zone" AS dropoff_zone,
    MAX(t.tip_amount) AS max_tip
FROM
    green_taxi_data t
JOIN
    zone_lookup pu_z ON t."PULocationID" = pu_z."LocationID"
JOIN
    zone_lookup do_z ON t."DOLocationID" = do_z."LocationID"
WHERE
    pu_z."Zone" = 'East Harlem North'
    AND t.lpep_pickup_datetime >= '2025-11-01'
    AND t.lpep_pickup_datetime < '2025-12-01'
GROUP BY
    1
ORDER BY
    2 DESC
LIMIT 1;
```

## Terraform (Optional)

If you want to use Terraform for infrastructure provisioning, you can add Terraform configurations in this directory. However, for this homework, Docker Compose is sufficient.

## Cleanup

To stop the services:

```bash
docker-compose down
```

To remove volumes (including data):

```bash
docker-compose down -v
```

## Notes

- The data ingestion script uses pandas to read Parquet files and SQLAlchemy to load data into PostgreSQL
- Zone lookup data is only loaded once (checks if table exists)
- All timestamps are in UTC
- Use pgAdmin to explore the data and run queries