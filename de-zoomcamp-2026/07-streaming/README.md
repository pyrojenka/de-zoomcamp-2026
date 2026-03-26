# Data Engineering Zoomcamp 2026 - Homework 7: Streaming Processing

This repository contains the solution for the Module 7 Homework (Streaming Processing) of the Data Engineering Zoomcamp 2026.

## Technologies Used
- Apache Flink (PyFlink for Python API)
- Apache Kafka (Redpanda for local setup)
- Docker (for environment setup)

## Project Overview

In this project, we practice streaming data processing using Apache Kafka (Redpanda) as a message broker and Apache Flink (PyFlink) for stream processing. We will be working with NYC Green Taxi Trip data to perform various streaming aggregations and analyses.

## Dataset

We use the **Green Taxi Trip Records** for **October 2025**.
- **Source:** [NYC Trip Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- **Direct Link:** [green_tripdata_2025-10.parquet](https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet)

## Project Structure

```text
├── README.md             # Project documentation (this file)
└── workshop/             # Dockerized environment and Flink jobs
    ├── docker-compose.yml
    ├── Dockerfile.flink
    ├── flink-config.yaml
    ├── Makefile
    ├── pyproject.flink.toml
    ├── pyproject.toml
    └── job/
        ├── five_min_aggregation_job.py
        ├── hourly_tips_job.py
        ├── pass_through_job.py
        └── session_window_job.py
    └── producers/
        └── producer.py
```

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for `uv` and local script execution)
- `uv` (Recommended for package management, if running producer locally)

### Installation
1. Navigate to the workshop directory:
   ```bash
   cd de-zoomcamp-2026/07-streaming/workshop
   ```

2. Build the Docker images and start the services:
   ```bash
   docker compose build
   docker compose up -d
   ```

3. If you previously ran the workshop and have old containers/volumes, perform a clean start:
   ```bash
   docker compose down -v
   docker compose build
   docker compose up -d
   ```

## Homework Tasks & Results

### 1. Redpanda Version

Run `rpk version` inside the Redpanda container:
```bash
docker exec -it workshop-redpanda-1 rpk version
```

### 2. Sending data to Redpanda

First, create a topic called `green-trips`:
```bash
docker exec -it workshop-redpanda-1 rpk topic create green-trips
```

Then, run the producer to send data to the topic:
```bash
uv run python src/producers/producer.py
```

### 3. Consumer - Trip Distance

Create a Flink SQL table for processed events:
```sql
CREATE TABLE processed_events (
    lpep_pickup_datetime TIMESTAMP,
    lpep_dropoff_datetime TIMESTAMP,
    PULocationID INTEGER,
    DOLocationID INTEGER,
    passenger_count DOUBLE PRECISION,
    trip_distance DOUBLE PRECISION,
    tip_amount DOUBLE PRECISION,
    total_amount DOUBLE PRECISION
);
```

Run the `pass_through_job.py` Flink job:
```bash
docker compose exec jobmanager ./bin/flink run \
    -py /opt/src/job/pass_through_job.py \
    --pyFiles /opt/src -d
```

Query to count trips with `trip_distance > 5.0`:
```sql
SELECT COUNT(*) FROM processed_events WHERE trip_distance > 5.0;
```

### 4. Tumbling Window - Pickup Location

Create a Flink SQL table for five-minute aggregated trips:
```sql
CREATE TABLE five_min_aggregated (
    window_start TIMESTAMP(3),
    PULocationID INT,
    num_trips BIGINT,
    PRIMARY KEY (window_start, PULocationID)
);
```

Run the `five_min_aggregation_job.py` Flink job:
```bash
docker compose exec jobmanager ./bin/flink run \
    -py /opt/src/job/five_min_aggregation_job.py \
    --pyFiles /opt/src -d
```

Query to find top 3 `PULocationID` by `num_trips`:
```sql
SELECT PULocationID, num_trips
FROM five_min_aggregated
ORDER BY num_trips DESC
LIMIT 3;
```

### 5. Session Window - Longest Streak

Create a Flink SQL table for session aggregated trips:
```sql
CREATE TABLE session_aggregated (
    window_start TIMESTAMP(3),
    PULocationID INT,
    num_trips BIGINT,
    PRIMARY KEY (window_start, PULocationID)
);
```

Run the `session_window_job.py` Flink job:
```bash
docker compose exec jobmanager ./bin/flink run \
    -py /opt/src/job/session_window_job.py \
    --pyFiles /opt/src -d
```

Query to find the maximum number of trips in a session:
```sql
SELECT MAX(num_trips) FROM session_aggregated;
```

### 6. Tumbling Window - Largest Tip

Create a Flink SQL table for hourly tips:
```sql
CREATE TABLE hourly_tips (
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    total_tips DOUBLE PRECISION,
    PRIMARY KEY (window_start, window_end)
);
```

Run the `hourly_tips_job.py` Flink job:
```bash
docker compose exec jobmanager ./bin/flink run \
    -py /opt/src/job/hourly_tips_job.py \
    --pyFiles /opt/src -d
```

Query to find top 5 entries by `total_tips`:
```sql
SELECT * FROM hourly_tips ORDER BY total_tips DESC LIMIT 5;
