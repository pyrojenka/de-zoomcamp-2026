# Data Engineering Zoomcamp 2026 - Homework 4: Analytics Engineering

This homework focuses on Analytics Engineering with dbt, using the NYC Taxi dataset (Yellow, Green, and FHV). The goal is to transform raw data into a clean, analytical schema using **dbt (data build tool)** and **Google BigQuery**.

---
## 📋 Prerequisites
Before running the project, ensure you have:
- **GCP Account** with BigQuery and Cloud Storage enabled.
- **dbt Core** (v1.7+) installed and configured (or dbt Cloud).
- **Python 3.9+** for data loading scripts.
## 🏗️ Project Structure
The dbt project is located in this directory (`04-analytics-engineering`) and follows a standard structure:
- `models/staging`: Raw data transformation (type casting, renaming).
- `models/core`: Fact and dimension tables joining multiple sources.
- `seeds/`: Reference data (e.g., taxi zone lookups).

## Setup Instructions

1. **Load Data**: Ensure Green and Yellow taxi data for 2019-2020 is loaded into your BigQuery dataset.
2. **dbt Project**: Configure the dbt project located in `04-analytics-engineering`.
3. **Build Models**: Run `dbt build --target prod` to create models in the production dataset.

```bash
dbt build --target prod
```

---

## Questions and Queries

### Question 1: dbt Lineage and Execution

Given the project structure with `stg_green_tripdata`, `stg_yellow_tripdata`, and `int_trips_unioned` (dependent on both staging models), we want to know what builds when running `dbt run --select int_trips_unioned`.

**Answer:** `int_trips_unioned` only

When using the `--select` flag without any modifiers (like `+` or `@`), dbt only runs the specific model(s) selected.

### Question 2: dbt Tests

A generic test for `payment_type` allows values `[1, 2, 3, 4, 5]`. A new value `6` appears in the source data.

**Answer:** dbt will fail the test, returning a non-zero exit code

By default, dbt tests fail if any records do not match the expected criteria (i.e., if `payment_type` is not in the accepted values list).

### Question 3: Counting Records in `fct_monthly_zone_revenue`

**Query:**
```sql
SELECT count(*) 
FROM `dbt_prod.fct_monthly_zone_revenue`;
```

### Question 4: Best Performing Zone for Green Taxis (2020)

Find the pickup zone with the highest total revenue for Green taxi trips in 2020.

**Query:**
```sql
SELECT 
    pickup_zone, 
    SUM(revenue_monthly_total_amount) as total_revenue
FROM `dbt_prod.fct_monthly_zone_revenue`
WHERE service_type = 'Green' 
  AND EXTRACT(YEAR FROM revenue_month) = 2020
GROUP BY pickup_zone
ORDER BY total_revenue DESC
LIMIT 1;
```

### Question 5: Green Taxi Trip Counts (October 2019)

Total number of trips for Green taxis in October 2019.

**Query:**
```sql
SELECT sum(total_monthly_trips)
FROM `dbt_prod.fct_monthly_zone_revenue`
WHERE service_type = 'Green' 
  AND EXTRACT(YEAR FROM revenue_month) = 2019
  AND EXTRACT(MONTH FROM revenue_month) = 10;
```

### Question 6: Build a Staging Model for FHV Data

**Step 1:** Upload the raw FHV data (2019) to the Google Cloud Storage bucket (`gs://nytaxi-dataset/fhv/`).
```bash
python load_fhv_ny_taxi_data.py
```
**Step 2:** Load the raw FHV data (2019) into BigQuery.
```sql
LOAD DATA OVERWRITE `nytaxi.fhv_tripdata_2019`
FROM FILES (
  format = 'CSV',
  uris = ['gs://nytaxi-dataset/fhv/fhv_tripdata_2019-*.csv.gz'],
  skip_leading_rows = 1
);
```

Create a staging model for FHV trip data (2019) with the following requirements:
- Filter out records where `dispatching_base_num` is NULL.
- Rename fields (e.g., `PUlocationID` to `pickup_location_id`).

```bash
dbt build --select stg_fhv_tripdata
```
**Query:**
```sql
SELECT count(*) FROM `dbt_prod.stg_fhv_tripdata`;
```
