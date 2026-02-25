# Data Engineering Zoomcamp 2026 - Workshop: dlt (data load tool)

This workshop focuses on building data pipelines using **dlt (data load tool)**. The goal is to ingest NYC Taxi trip data from a custom REST API into **DuckDB** and perform basic analytical queries on the loaded data.

---

## 📋 Workshop Resources

*   [Workshop README](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/workshops/dlt/README.md)
*   [dlt Pipeline Overview Notebook (Google Colab)](https://colab.research.google.com/github/anair123/data-engineering-zoomcamp/blob/workshop/dlt_2026/cohorts/2026/workshops/dlt/dlt_Pipeline_Overview.ipynb)
*   [dlt Documentation](https://dlthub.com/docs)

## 🏗️ The Challenge

Build a dlt pipeline from scratch that loads NYC Yellow Taxi trip data from a custom API into a local DuckDB instance. Unlike standard dlt scaffolds, this requires manual configuration of the REST API source, including handling pagination.

## 📊 Data Source

The dataset contains records of individual taxi trips in New York City.

| Property | Value |
| :--- | :--- |
| **Base URL** | `https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api` |
| **Format** | Paginated JSON |
| **Page Size** | 1,000 records per page |
| **Pagination** | Stop when an empty page is returned |

---

## 🛠️ Setup Instructions

### 1. Install uv (if you don't have it)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Initialize the project
Create a new directory and set up your environment:
```bash
mkdir taxi-pipeline
cd taxi-pipeline
uv sync
```

### 3. Initialize the Pipeline Scaffold
```bash
uv run dlt init dlthub:taxi_pipeline duckdb
```

### 4. Set Up dlt MCP Server
Add the dlt MCP server to your environment to give your AI assistant access to dlt documentation and your pipeline metadata:
```bash
claude mcp add dlt -- uv run --with "dlt[duckdb]" --with "dlt-mcp[search]" python -m dlt_mcp
```

### 5. Implementation
Create `taxi_pipeline.py` with the REST API configuration. Key configurations include:
*   `base_url`: The API endpoint.
*   `paginator`: Use `PageNumberPaginator` with `base_page=1` and `total_path=None`.
*   `write_disposition`: Set to `replace`.

### 6. Run the Pipeline
```bash
uv run python taxi_pipeline.py
```

---

## ❓ Questions and Queries

Once the pipeline has run successfully, use the methods covered in the workshop to investigate the following:

- **dlt Dashboard**: `uv run dlt pipeline taxi_pipeline show`
  *(Open the "Dataset Browser" tab to inspect data and source/resource state).*

### Question 1: What is the start date and end date of the dataset?

**Query:**
```sql
SELECT 
    MIN(trip_pickup_date_time) AS start_date,
    MAX(trip_dropoff_date_time) AS end_date
FROM rides;
```

**Answer:** `2009-06-01` to `2009-07-01`

### Question 2: What proportion of trips are paid with credit card?

**Query:**
```sql
SELECT 
    ROUND(SUM(CASE WHEN payment_type = 'Credit' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS credit_card_pct
FROM rides;
```

**Answer:** `26.66%`

### Question 3: What is the total amount of money generated in tips?

**Query:**
```sql
SELECT 
    ROUND(SUM(tip_amt), 2) AS total_tips 
FROM rides;
```

**Answer:** `$6,063.41`

