# Data Engineering Zoomcamp 2026 - Homework 4: Analytics Engineering

This homework focuses on Analytics Engineering with dbt, using the NYC Taxi dataset (Yellow, Green, and FHV) to transform data and build analytical models.

## Setup Instructions

1. **Load Data**: Ensure Green and Yellow taxi data for 2019-2020 is loaded.
2. **dbt Project**: Configure the dbt project located in `04-analytics-engineering/taxi_rides_ny/`.
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
FROM `taxi-rides-ny.nytaxi.fct_monthly_zone_revenue`;
```

**Answer:** 12,184

### Question 4: Best Performing Zone for Green Taxis (2020)

Find the pickup zone with the highest total revenue for Green taxi trips in 2020.

**Query:**
```sql
SELECT 
    pickup_zone, 
    revenue_monthly_total_amount
FROM `taxi-rides-ny.nytaxi.fct_monthly_zone_revenue`
WHERE service_type = 'Green' 
  AND EXTRACT(YEAR FROM pickup_datetime) = 2020
ORDER BY revenue_monthly_total_amount DESC
LIMIT 1;
```

**Answer:** East Harlem North

### Question 5: Green Taxi Trip Counts (October 2019)

Total number of trips for Green taxis in October 2019.

**Query:**
```sql
SELECT sum(total_monthly_trips)
FROM `taxi-rides-ny.nytaxi.fct_monthly_zone_revenue`
WHERE service_type = 'Green' 
  AND EXTRACT(YEAR FROM pickup_datetime) = 2019
  AND EXTRACT(MONTH FROM pickup_datetime) = 10;
```

**Answer:** 384,624

### Question 6: Build a Staging Model for FHV Data

Create a staging model for FHV trip data (2019) with the following requirements:
- Filter out records where `dispatching_base_num` is NULL.
- Rename fields (e.g., `PUlocationID` to `pickup_location_id`).

**Query:**
```sql
SELECT count(*) FROM `taxi-rides-ny.nytaxi.stg_fhv_tripdata`;
```

**Answer:** 43,244,693
