-- taxi mobility database --

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS zone_shapes;
DROP TABLE IF EXISTS zones;
DROP TABLE IF EXISTS boroughs;
DROP TABLE IF EXISTS vendors;
DROP TABLE IF EXISTS rate_codes;
DROP TABLE IF EXISTS payment_types;

-- TABLES --
CREATE TABLE vendors(
    vendor_id INTEGER PRIMARY KEY,
    vendor_name TEXT NOT NULL
);

INSERT INTO vendors (vendor_id, vendor_name) VALUES
(1, 'Create Mobile Technologies'),
(2, 'VeriFone Inc.'),
(4, 'Unknown vendor (code 4)');

CREATE TABLE rate_codes(
    rate_code_id INTEGER PRIMARY KEY,
    description TEXT NOT NULL
);

INSERT INTO rate_codes ( rate_code_id, description) VALUES
(1, 'Standard rate'),
(2, 'JFK'),
(3, 'Newark'),
(4, 'Nassau or Westchester'),
(5, 'Negotiated fare'),
(6, 'Group ride');

CREATE TABLE payment_types (
    payment_type_id INTEGER PRIMARY KEY,
    description TEXT NOT NULL
);

INSERT INTO payment_types (payment_type_id, description) VALUES
(1, 'Credit card'),
(2, 'Cash'),
(3, 'No charge'),
(4, 'Dispute'),
(5, 'Unknown'),
(6, 'Voided trip');

-- location tables --

CREATE TABLE boroughs (
    borough_id INTEGER PRIMARY KEY AUTOINCREMENT,
    borough_name TEXT NOT NULL UNIQUE
);

CREATE TABLE zones (
    location_id INTEGER PRIMARY KEY,
    zone_name TEXT NOT NULL,
    borough_id INTEGER NOT NULL REFERENCES boroughs(borough_id),
    service_zone TEXT NOT NULL
);

CREATE TABLE zone_shapes(
    shape_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL REFERENCES zones(location_id),
    geojson TEXT NOT NULL
);

CREATE TABLE trips(
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL REFERENCES vendors(vendor_id),
    rate_code_id          INTEGER NOT NULL REFERENCES rate_codes(rate_code_id),
    payment_type_id       INTEGER NOT NULL REFERENCES payment_types(payment_type_id),
    pu_location_id        INTEGER NOT NULL REFERENCES zones(location_id),
    do_location_id        INTEGER NOT NULL REFERENCES zones(location_id),
    
    -- when (ISO text sorts coirrectly)
    pickup_datetime  TEXT NOT NULL,
    dropoff_datetime TEXT NOT NULL,

    -- trip details
    passenger_count       INTEGER NOT NULL CHECK (passenger_count BETWEEN 1 AND 6),
    trip_distance         REAL    NOT NULL CHECK (trip_distance > 0),
    store_and_fwd_flag    TEXT    NOT NULL CHECK (store_and_fwd_flag IN ('Y', 'N')),

    -- money 
    fare_amount           REAL    NOT NULL CHECK (fare_amount > 0),
    extra                 REAL    NOT NULL DEFAULT 0,
    mta_tax               REAL    NOT NULL DEFAULT 0,
    tip_amount            REAL    NOT NULL DEFAULT 0,
    tolls_amount          REAL    NOT NULL DEFAULT 0,
    improvement_surcharge REAL    NOT NULL DEFAULT 0,
    congestion_surcharge  REAL    NOT NULL DEFAULT 0,
    total_amount          REAL    NOT NULL CHECK (total_amount > 0),

    -- lderived features 
    trip_duration_min     REAL    NOT NULL,
    avg_speed_mph         REAL    NOT NULL,
    fare_per_mile         REAL,   -- NULL for trips under 0.5 miles
    tip_pct               REAL,   -- NULL for non-card payments
    pickup_hour           INTEGER NOT NULL CHECK (pickup_hour BETWEEN 0 AND 23),
    pickup_weekday        INTEGER NOT NULL CHECK (pickup_weekday BETWEEN 0 AND 6),
    is_weekend            INTEGER NOT NULL CHECK (is_weekend IN (0, 1)),
    time_of_day           TEXT    NOT NULL,
    is_airport_trip       INTEGER NOT NULL CHECK (is_airport_trip IN (0, 1)),
    is_cross_borough      INTEGER NOT NULL CHECK (is_cross_borough IN (0, 1)),

    CHECK (dropoff_datetime > pickup_datetime)
);

-- indexes ( match dashboard filters)
CREATE INDEX idx_trips_pickup_datetime ON trips(pickup_datetime);
CREATE INDEX idx_trips_pickup_hour     ON trips(pickup_hour);
CREATE INDEX idx_trips_pu_location     ON trips(pu_location_id);
CREATE INDEX idx_trips_do_location     ON trips(do_location_id);
CREATE INDEX idx_trips_fare            ON trips(fare_amount);
CREATE INDEX idx_trips_distance        ON trips(trip_distance);
CREATE INDEX idx_zones_borough         ON zones(borough_id);
CREATE INDEX idx_zone_shapes_location  ON zone_shapes(location_id);



