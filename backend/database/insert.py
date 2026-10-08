import sqlite3
import os
import pandas as pd
import sys 
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from pipeline.load import load_trips, load_zone_lookup
from pipeline.clean import clean_trips, clean_zone_lookup
from pipeline.features import add_features 


DB_PATH = os.path.join(os.path.dirname(__file__), "mobility_data.db")
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")

class DataCleaningLogger:
    def log(self, df, reason, action):
        pass
def populate_database():
    conn = sqlite3.connect(DB_PATH)

    zones_raw = load_zone_lookup()
    zones_clean = clean_zone_lookup(zones_raw)
    zones_clean.rename(columns={
        'locationID': 'location_id',
        'Borough': 'borough',
        'Zone': 'zone',
        'service_zone': 'service_zone' 
    }, inplace=True)
    zones_clean.to_sql('taxi_zones', conn, if_exists='replace', index=False)

    trips_raw = load_trips()
    valid_zone_ids = set(zones_raw['LocationID'])
    logger = DataCleaningLogger()
    trips_clean = clean_trips(trips_raw, valid_zone_ids, logger)
    trips_featured = add_features(trips_clean, zones_clean)

    trips_featured.rename(columns={
        'PUlocationID': 'pu_location_id',
         'DOlocationID': 'do_location_id',
         'RatecodeID': 'vendor_id',
   }, inplace=True)

    trips_featured.to_sql('trips', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    populate_database()