"""Pipeline to ingest NYC taxi data from REST API into DuckDB using dlt."""

import dlt
from dlt.sources.rest_api import rest_api_source


def taxi_source():
    """Define a REST API source for NYC taxi data."""
    source = rest_api_source(
        {
            "client": {
                "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net",
            },
            "resource_defaults": {
                "write_disposition": "replace",
            },
            "resources": [
                {
                    "name": "rides",
                    "endpoint": {
                        "path": "data_engineering_zoomcamp_api",
                        "paginator": {
                            "type": "page_number",
                            "base_page": 1,
                            "page_param": "page",
                            "total_path": None,
                            "stop_after_empty_page": True,
                        },
                    },
                },
            ],
        }
    )
    return source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="taxi_pipeline",
        destination="duckdb",
        dataset_name="taxi_rides",
    )

    load_info = pipeline.run(taxi_source())
    print(load_info)  # noqa: T201
