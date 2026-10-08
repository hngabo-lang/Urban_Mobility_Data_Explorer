CREATE TABLE IF NOT EXISTS taxi_zones (
    location_id INTEGER PRIMARY KEY,
    borough TEXT,
    zone TEXT,
    service_zone TEXT
);
CREATE TABLE IF NOT EXISTS trips (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER,
    tpep_pickup_datetime DATETIME,
    tpep_dropoff_datetime DATETIME,
    passenger_count INTEGER,
    trip_distance REAL,
    rate_code_id INTEGER,
    store_and_fwd_flag TEXT,
    pu_location_id INTEGER,
    do_location_id INTEGER,
    payment_type INTEGER,
    fare_amount REAL,
    extra REAL,
    mta_tax REAL,
    trip_amount REAL,
    tolls_amount REAL,
    improvement_surcharge REAL,
    total_amount REAL,
    congestion_surcharge REAL,
    airport_fee REAL,
    trip_duration_min REAL,
    avg_speed_mph REAL,
    fare_per_mile REAL,
    tip_percentage REAL,
    FOREIGN KEY (pu_location_id) REFERENCES taxi_zones(location_id),
    FOREIGN KEY (do_location_id) REFERENCES taxi_zones(location_id)
);

CREATE INDEX IF NOT EXISTS idx_trips_pickup_dt ON trips(tpep_pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_trips_pu_location ON trips(pu_location_id);
CREATE INDEX IF NOT EXISTS idx_trips_do_location ON trips(do_location_id);
CREATE INDEX IF NOT EXISTS idx_trips_fare ON trips(fare_amount);




