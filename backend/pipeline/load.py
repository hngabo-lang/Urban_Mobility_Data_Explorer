import sys
from pathlib import Path

import pandas as pd
import geopandas as gpd

# allow import
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

# functions
def load_trips():
    return pd.read_csv(
        config.TRIPS_FILE,
        nrows=config.SAMPLE_ROWS,
        parse_dates=["tpep_pickup_datetime", "tpep_dropoff_datetime"],
        low_memory = False,
    )

def load_zone_lookup():
    return pd.read_csv(config.ZONE_LOOKUP_FILE)

def load_zone_shapes():
    path = config.ZONE_SPATIAL_FILE
    if path.is_dir():
        shp_files = list(path.glob("*.shp"))
        if not shp_files:
            raise FileNotFoundError(f"No .shp file found in {path}")
        path = shp_files[0]
    gdf = gpd.read_file(path)

    # convert to standard lat/lon so web map can draw it
    return gdf.to_crs(epsg=4326)

def explore(df,name):
    print(f"\n===={name}=====")
    print(f"Rows: {len(df):,} Column: {len(df.columns)}")
    print("\n Column types:")
    print(df.dtypes)
    print("\n Missing values per column:")
    print(df.isna().sum())
    print("\n First 5 rows:")
    print(df.head(5))

if __name__ == "__main__":
    trips = load_trips()
    explore(trips, "TRIPS")
    print("\n Numeric summary (look for negative and huge values):")
    print(trips.describe().T)
    print(f"\n Duplicate rows: {trips.duplicated().sum()}")

    lookup = load_zone_lookup()
    explore(lookup, "ZONE LOOKUP")

    shapes = load_zone_shapes()
    print(f" \n ===== ZONE SHAPES=======\n Zones: {len(shapes)}")
    print(shapes.drop(columns="geometry").head(5))