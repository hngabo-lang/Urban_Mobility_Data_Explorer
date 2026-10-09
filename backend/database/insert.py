import json
import sys 
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from database.db import get_connection, init_db
from pipeline.load import load_trips, load_zone_lookup, load_zone_shapes
from pipeline.clean import clean_trips, clean_zone_lookup
from pipeline.features import add_features 
from pipeline.logger import RecordLogger


# columns in the trips table


BOOL_COLUMNS = ["is_weekend", "is_airport_trip", "is_cross_borough"]
TRIP_COLUMNS = [
    "vendor_id", "rate_code_id", "payment_type_id",
    "pu_location_id", "do_location_id",
    "pickup_datetime", "dropoff_datetime",
    "passenger_count", "trip_distance", "store_and_fwd_flag",
    "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount",
    "improvement_surcharge", "congestion_surcharge", "total_amount",
    "trip_duration_min", "avg_speed_mph", "fare_per_mile", "tip_pct",
    "pickup_hour", "pickup_weekday", "is_weekend", "time_of_day",
    "is_airport_trip", "is_cross_borough",
]

# insert each borough once

def insert_boroughs(conn, zones):
    names = sorted(zones["borough"].unique())
    conn.executemany(
        "INSERT INTO boroughs (borough_name) VALUES (?)",
        [(name,) for name in names],
         )
    
    rows = conn.execute("SELECT borough_id, borough_name FROM boroughs")
    return {row["borough_name"]: row["borough_id"] for row in rows}

def insert_zones(conn, zones, borough_ids):
    rows = [
        (int(z.location_id), z.zone, borough_ids[z.borough], z.service_zone)
        for z in zones.itertuples()
    ]
    conn.executemany(
        "INSERT INTO zones (location_id, zone_name, borough_id, service_zone) "
        "VALUES (?, ?, ?, ?)",
        rows,
    )

# Store each polygon as GeoJSON text 
def insert_zone_shapes(conn, shapes):
    shapes = shapes[["LocationID", "geometry"]].copy()
    shapes["geometry"] = shapes.geometry.simplify(0.0001)
    rows = [
        (int(s.LocationID), json.dumps(s.geometry.__geo_interface__))
        for s in shapes.itertuples()
    ]
    conn.executemany(
        "INSERT INTO zone_shapes (location_id, geojson) VALUES (?, ?)",
        rows,
    )

    # match dataframe to trips table
 
def prepare_trips(trips):
    df = trips.rename(columns={"payment_type" : "payment_type_id"})
    for col in ["pickup_datetime", "dropoff_datetime"]:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
    for col in BOOL_COLUMNS:
        df[col] = df[col].astype(int)
    return df[TRIP_COLUMNS]

def insert_trips(conn,trips):
    trips.to_sql("trips", conn, if_exists= "append", index = False, chunksize=50_000)

def populate_database():
    logger = RecordLogger()

    print("Loading, cleaning and adding features...")
    zones = clean_zone_lookup(load_zone_lookup())
    trips = clean_trips(load_trips(), set(zones["location_id"]), logger)
    trips = add_features(trips, zones)
    shapes = load_zone_shapes()

    print("Resetting database")
    init_db()

    conn = get_connection()
    try:
        print("Inserting boroughs and zones .... ")
        borough_ids = insert_boroughs(conn, zones)
        insert_zones(conn, zones, borough_ids)
        insert_zone_shapes(conn, shapes)

        print(f"Inserting {len(trips):,} trips ....")
        insert_trips(conn, prepare_trips(trips))
        conn.commit()

        for table in ["boroughs", "zones","zone_shapes", "trips"]:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{table}: {count:,} rows")
    finally:
        conn.close()


    logger.save()
    print(f"Done. Database at {config.DB_PATH}")


if __name__ == "__main__":
    populate_database()



