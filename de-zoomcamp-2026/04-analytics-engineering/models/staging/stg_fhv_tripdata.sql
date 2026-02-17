with source as 
(
  select *,
    row_number() over(partition by dispatching_base_num, pickup_datetime) as rn
  from {{ source('raw', 'fhv_tripdata_2019') }}
  where dispatching_base_num is not null
)
select
    -- identifiers
    cast(dispatching_base_num as string) as dispatching_base_num,
    cast(pulocationid as integer) as pickup_location_id,
    cast(dolocationid as integer) as dropoff_location_id,
    
    -- timestamps
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropoff_datetime as timestamp) as dropoff_datetime,
    
    -- additional info
    cast(sr_flag as string) as sr_flag,
    cast(affiliated_base_number as string) as affiliated_base_number

from source
