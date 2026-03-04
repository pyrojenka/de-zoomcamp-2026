# Data Engineering Zoomcamp 2026 - Data Platforms (Bruin)

This directory contains an end-to-end data pipeline for NYC Taxi datasets using [Bruin](https://getbruin.com) - a unified CLI tool for data ingestion, transformation, orchestration, and quality. The pipeline uses DuckDB as a local data warehouse and follows a layered architecture (Ingestion -> Staging -> Reports).

## Prerequisites ✅

- **Bruin CLI**: Install via `curl -LsSf https://getbruin.com/install/cli | sh`
- **Python 3.11+**: Required for ingestion assets
- **DuckDB CLI** (optional): For interactive data exploration
- **Bruin VS Code Extension** (highly recommended): For visual lineage and action buttons

## Project Structure 📁

```text
my-taxi-pipeline/
├── .bruin.yml                 # Environment and connection configuration
├── README.md                  # Setup and usage guide
├── duckdb.db                  # Local DuckDB database (generated after run)
└── pipeline/
    ├── pipeline.yml           # Pipeline metadata, schedule, and variables
    └── assets/
        ├── ingestion/         # Layer 1: Raw data extraction
        │   ├── trips.py       # Python-based API ingestion
        │   ├── requirements.txt
        │   ├── payment_lookup.asset.yml
        │   └── payment_lookup.csv
        ├── staging/           # Layer 2: Cleaning and enrichment
        │   └── trips.sql      # SQL transformation with deduplication
        └── reports/           # Layer 3: Analytics and aggregation
            └── trips_report.sql
```

## Setup Instructions 🔧

### 1. Initialize the project
If starting from scratch:
```bash
bruin init zoomcamp my-taxi-pipeline
cd my-taxi-pipeline
```

### 2. Configure Connections
Ensure your `.bruin.yml` has the local DuckDB connection defined:
```yaml
default_environment: default
environments:
  default:
    connections:
      duckdb:
        - name: duckdb-default
          path: duckdb.db
```

### 3. Install Dependencies
Bruin automatically manages environments for Python assets. Ensure `requirements.txt` in the ingestion folder includes:
- `pandas`
- `requests`
- `pyarrow`
- `python-dateutil`

## How to run the pipeline ▶️

### Validate the pipeline
Always validate before running to catch syntax or dependency errors:
```bash
bruin validate pipeline/
```

### Initial Run (Full Refresh)
When running for the first time or after a schema change, use `--full-refresh` to create tables:
```bash
bruin run --full-refresh --start-date 2025-01-01 --end-date 2025-01-31 pipeline/
```

### Running Specific Layers
To run only ingestion and all its downstream assets:
```bash
bruin run --select ingestion.trips+ --start-date 2025-01-01
```

### Overriding Variables
Process only yellow taxis by overriding the `taxi_types` variable:
```bash
bruin run --var 'taxi_types=["yellow"]' pipeline/
```

## Querying Data 🧾

Use the `bruin query` command to inspect your tables:

- **Check ingestion row count:**
```bash
bruin query --connection duckdb-default --query "SELECT COUNT(*) FROM ingestion.trips"
```

- **Inspect staging trips:**
```bash
bruin query --connection duckdb-default --query "SELECT * FROM staging.trips LIMIT 10"
```

- **View top payment types from report:**
```bash
bruin query --connection duckdb-default --query "SELECT payment_type, SUM(trip_count) FROM reports.trips_report GROUP BY 1 ORDER BY 2 DESC"
```

## Lineage and Quality 🧭

- **View Lineage**: Use `bruin lineage pipeline/assets/reports/trips_report.sql` to see the end-to-end dependency graph.
- **Quality Checks**: This pipeline includes built-in checks (`not_null`, `unique`, `positive`) and custom checks (`row_count_greater_than_zero`). They run automatically after each asset execution.

## Notes 💡

- **Date Range**: NYC Taxi data availability ends in late 2025. Use January 2025 for reliable testing.
- **Performance**: Parquet files are large. Ingesting 1-2 months is recommended for development.
- **Idempotency**: The `time_interval` strategy ensures that re-running the same period deletes old data before inserting new data, avoiding duplicates.