# Data Engineering Zoomcamp 2026 - Workflow Orchestration (Kestra)

This directory contains flows and configurations to orchestrate data ingestion and backfills for NYC taxi datasets using Kestra. The README follows the style from `01-docker-terraform` and includes setup, how to run flows, and troubleshooting tips.

## Prerequisites ✅

- Docker and Docker Compose
- Java (required by Kestra image if running outside Docker)
- Kestra image is included in the `docker-compose.yaml` in this folder
- A GCP service account JSON with permissions for BigQuery and GCS (if using GCP tasks)

## Project Structure 📁

```
02-workflow-orchestration/
├── README.md
├── docker-compose.yaml
├── service-account.json (optional, keep locally)
├── .env_encoded (generated)
└── flows/
    ├── 01_gcp_kv.yaml
    ├── 02_gcp_setup.yaml
    ├── 03_gcp_taxi.yaml
    └── 04_flow_orchestrator.yaml
```

## Setup Instructions 🔧

### 1. Add Service Account as an encoded secret

Rename your downloaded service account file to `service-account.json` then run:

```bash
# encode and add to .env_encoded
echo SECRET_GCP_SERVICE_ACCOUNT=$(cat service-account.json | base64 -w 0) >> .env_encoded
```

This project reads `SECRET_GCP_SERVICE_ACCOUNT` from `.env_encoded` and injects it into the Kestra container as a secret used by GCP plugins.

### 2. Start Kestra and supporting services

From this directory:

```bash
docker-compose up -d
```

Services started include:
- PostgreSQL for Kestra and metadata
- Kestra server (web UI at http://localhost:8080)

### 3. Validate & upload flows

Open the Kestra UI, go to Flows → Upload or create flows using the YAML files under `flows/`.

## How to run the flow orchestrator ▶️

- `04_flow_orchestrator.yaml` is the parent flow that triggers taxi flows for given taxi types and months.
- The orchestrator loops over taxi types and months using nested `ForEach` and triggers `03_gcp_taxi` as a `Subflow`.

Run from the UI by starting the `04_flow_orchestrator` flow.

## Backfill details & inputs 🧭

- `03_gcp_taxi` accepts inputs: `taxi` ("yellow" | "green"), and optional `year` (YYYY) and `month` (MM).
- When `year` and `month` are provided, the flow computes a `backfill_date` and uses that for file names and table partitioning. If omitted, it falls back to `trigger.date` (useful for scheduled runs).

Example: orchestrator passes `taxi: "yellow"`, `year: "2021"`, `month: "03"` to process `yellow_tripdata_2021-03.csv`. 

## SQL queries (examples) 🧾

- Count rows for Yellow Taxi in 2020:

```sql
SELECT COUNT(*) FROM `your_project_id.zoomcamp.yellow_tripdata`
WHERE filename LIKE 'yellow_tripdata_2020-%.csv';
```

- Count rows for Green Taxi in 2020:

```sql
SELECT COUNT(*) FROM `your_project_id.zoomcamp.green_tripdata`
WHERE filename LIKE 'green_tripdata_2020-%.csv';
```

## Cleanup

To stop services:

```bash
docker-compose down
```

To remove volumes (data):

```bash
docker-compose down -v
```

## Notes 💡

- Keep `service-account.json` out of version control. Use `.env_encoded` for local development only.
- Use descriptive labels in Kestra flows (e.g., `backfill:true`) for easier filtering and monitoring.
