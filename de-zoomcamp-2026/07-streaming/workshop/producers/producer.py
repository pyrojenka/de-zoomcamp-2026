import json
from time import time
import pandas as pd
from kafka import KafkaProducer

# Download NYC green taxi trip data
url = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet"
columns = [
    'lpep_pickup_datetime',
    'lpep_dropoff_datetime',
    'PULocationID',
    'DOLocationID',
    'passenger_count',
    'trip_distance',
    'tip_amount',
    'total_amount'
]
df = pd.read_parquet(url, columns=columns)
df['passenger_count'] = df['passenger_count'].fillna(0)
df['tip_amount'] = df['tip_amount'].fillna(0)

def json_serializer(data):
    return json.dumps(data).encode('utf-8')

server = 'localhost:9092'

producer = KafkaProducer(
    bootstrap_servers=[server],
    value_serializer=json_serializer
)

t0 = time()
topic_name = 'green-trips'

for _, row in df.iterrows():
    ride_dict = row.to_dict()
    
    # Convert datetime columns to strings for JSON serialization
    ride_dict['lpep_pickup_datetime'] = str(ride_dict['lpep_pickup_datetime'])
    ride_dict['lpep_dropoff_datetime'] = str(ride_dict['lpep_dropoff_datetime'])
    
    producer.send(topic_name, value=ride_dict)

producer.flush()

t1 = time()
print(f'took {(t1 - t0):.2f} seconds')
