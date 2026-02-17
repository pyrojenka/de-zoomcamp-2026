import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage
from google.api_core.exceptions import NotFound, Forbidden
import time

# Change this to your bucket name
BUCKET_NAME = "nytaxi-dataset"

# If you authenticated through the GCP SDK you can comment out these two lines
CREDENTIALS_FILE = "service-account.json"

if os.path.exists(CREDENTIALS_FILE):
    client = storage.Client.from_service_account_json(CREDENTIALS_FILE)
else:
    print(f"Warning: '{CREDENTIALS_FILE}' not found. Falling back to Application Default Credentials.")
    client = storage.Client()
# If commented initialize client with the following
# client = storage.Client(project='zoomcamp-mod3-datawarehouse')


BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/"
MONTHS = [f"{i:02d}" for i in range(1, 13)]
DOWNLOAD_DIR = "."

CHUNK_SIZE = 8 * 1024 * 1024

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

bucket = client.bucket(BUCKET_NAME)


def download_file(month):
    filename = f"fhv_tripdata_2019-{month}.csv.gz"
    url = f"{BASE_URL}{filename}"
    file_path = os.path.join(DOWNLOAD_DIR, filename)

    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, file_path)
        print(f"Downloaded: {file_path}")
        return file_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None


def verify_gcs_upload(blob_name):
    return storage.Blob(bucket=bucket, name=blob_name).exists(client)


def upload_to_gcs(file_path, max_retries=3):
    blob_name = f"fhv/{os.path.basename(file_path)}"
    blob = bucket.blob(blob_name)
    blob.chunk_size = CHUNK_SIZE

    for attempt in range(max_retries):
        try:
            print(f"Uploading {file_path} to {BUCKET_NAME} (Attempt {attempt + 1})...")
            blob.upload_from_filename(file_path)
            print(f"Uploaded: gs://{BUCKET_NAME}/{blob_name}")

            if verify_gcs_upload(blob_name):
                print(f"Verification successful for {blob_name}")
                return
            else:
                print(f"Verification failed for {blob_name}, retrying...")
        except Exception as e:
            print(f"Failed to upload {file_path} to GCS: {e}")

        time.sleep(5)

    print(f"Giving up on {file_path} after {max_retries} attempts.")


if __name__ == "__main__":
    # db: bucket already created
    # create_bucket(BUCKET_NAME)

    with ThreadPoolExecutor(max_workers=4) as executor:
        file_paths = list(executor.map(download_file, MONTHS))

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(upload_to_gcs, filter(None, file_paths))  # Remove None values

    print("All files processed and verified.")