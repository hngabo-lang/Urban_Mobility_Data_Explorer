from pathlib import Path

# project root = folder above backend
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
LOGS_DIR = BASE_DIR / "logs"

# raw files
TRIPS_FILE = RAW_DIR / "yellow_tripdata_2019-01.csv"
ZONE_LOOKUP_FILE = RAW_DIR / "taxi_zone_lookup.csv"
ZONE_SPATIAL_FILE = RAW_DIR / "taxi_zones.shp"

# quick testing
SAMPLE_ROWS = 500_000

# databse 
DB_PATH = BASE_DIR / "backend" / "taxi.db"

# output
EXCLUDED_LOG = LOGS_DIR / "excluding_records.csv"
