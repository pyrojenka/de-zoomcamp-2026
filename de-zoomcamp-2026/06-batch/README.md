# Data Engineering Zoomcamp 2026 - Homework 6: Batch Processing

This repository contains the solution for the Module 6 Homework (Batch Processing) of the Data Engineering Zoomcamp 2026.

## Technologies Used
- PySpark (for data processing)
- Jupyter Notebook (for interactive development and analysis)
- `uv` (for dependency management and running the notebook)

## Project Overview

In this project, we process NYC Yellow Taxi trip data from November 2025 using PySpark. The tasks include:
- Initializing a Spark Session.
- Loading Parquet data.
- Repartitioning the dataset for optimized storage, improving read performance.
- Performing data transformations and aggregations (filtering by date, calculating trip duration).
- Joining trip data with zone lookup information to enrich the dataset.

## Dataset

We use the **Yellow Taxi Trip Records** for **November 2025**.
- **Source:** [NYC Trip Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- **Direct Link:** [yellow_tripdata_2025-11.parquet](https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet)
- **Zone Lookup:** [taxi_zone_lookup.csv](https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv)

## Project Structure

```text
├── 06-batch.ipynb        # Main Jupyter notebook with Spark logic
├── pyproject.toml        # Project dependencies (uv/pip)
├── data/                 # Processed data output directory
└── README.md             # Project documentation
```

## Setup and Installation

### Prerequisites
- Python 3.13+
- Java 8/11/17 (Required for Spark)
- [uv](https://github.com/astral-sh/uv) (Recommended for package management)

### Installation
1. Navigate to the project directory:
   ```bash
   cd de-zoomcamp-2026/06-batch
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

### Running the Notebook
1. Start Jupyter Notebook:
   ```bash
   uv run jupyter notebook
   ```
2. Your web browser should open automatically, displaying the Jupyter interface.
3. Open `06-batch.ipynb` from the file browser and execute the cells to see the results.

## Homework Tasks & Results

1. **Spark Version:** 4.1.1
2. **Repartitioning:** Data was repartitioned into 4 files (approx. 25MB each).
3. **Record Count (Nov 15th):** 162,604 trips.
4. **Longest Trip:** 90.65 hours.
5. **Least Frequent Pickup Zone:** Governor's Island/Liberty Island/Ellis Island (1 trip).
