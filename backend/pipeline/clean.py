
import sys
from pathlib import Path
import pandas as pd


sys.path.append(str(Path(__file__).resolve().parent.parent))

from pipeline.load import load_trips, load_zone_lookup
from pipeline.logger import RecordLogger

# Rules

DATA_START = pd.Timestamp("2019-01-01")
DATA_END = pd.Timestamp("2019-02-01")

MIN_DURATION_MIN = 1
MAX_DURATION_MIN = 240
MAX_DISTANCE_MI = 100
MAX_SPEED_MPH = 80
MAX_FARE = 500
MIN_FARE = 2.50
MAX_TOLLS = 100
MAX_PASSENGERS = 6

VALID_RATES_CODES = {1, 2, 3, 4, 5, 6}
VALID_PAYMENT_TYPES = {1, 2, 3, 4, 5, 6}

# raw names
COLUMN_RENAMES = {
    "VendorID" : "vendor_id",
    "tpep_pickup_datetime" : "pickup_datetime",
    "tpep_dropoff_datetime" : "dropoff_datetime",
    "RatecodeID" : "rate_code_id",
    "PULocationID" : "pu_location_id",
    "DOLocationID" : "do_location_id",
}

MONEY_COLUMNS = [
    "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", 
    "improvement_surcharge", "total_amount", "congestion_surcharge",
]

INT_COLUMNS = [
    "vendor_id", "passenger_count", "rate_code_id",
    "pu_location_id", "do_location_id", "payment_type",
]

HELPER_COLUMNS = ["_reason", "_duration_min", "_speed_mph"]

# mark rows that fails the rule

def flag( df, mask, reason):
    df.loc[mask & df["_reason"].isna(),"_reason"] = reason

# standardize the zone lookup
def clean_zone_lookup(lookup):
    lookup = lookup.rename(columns={
        "LocationID" : "location_id", "Borough": "borough",
        "Zone" : "zone", "service_zone" : "service_zone",
    })

    for col in ["borough", "zone", "service_zone"]:
        lookup[col] = lookup[col].fillna("UNKNOWN").str.strip()
    return lookup

def clean_trips(df, valid_zone_ids, logger):
    df = df.rename(columns=COLUMN_RENAMES)
    df["_reason"] = pd.NA

        # extract duploicate rows
    flag(df, df.drop(columns="_reason").duplicated(), "duplicate row")

        # missing critical values
    critical = ["vendor_id", "pickup_datetime", "dropoff_datetime", 
                    "pu_location_id", "do_location_id", "trip_distance",
                    "fare_amount", "total_amount"]
    flag (df, df[critical].isna().any(axis=1), "missing critcal value")

        # pickup otside this month
    outside = (df["pickup_datetime"] < DATA_START) | (df["pickup_datetime"] >= DATA_END)
    flag(df,outside, "pickup outside january 2019")

        # impossible or unrealistic durations
    df["_duration_min"] = (
            df['dropoff_datetime'] - df["pickup_datetime"]).dt.total_seconds() / 60
    flag(df,df["_duration_min"] <= 0, "dropoff not after pickup")
    flag(df,df["_duration_min"] < MIN_DURATION_MIN, "trip under 1 minute")
    flag(df, df["_duration_min"] > MAX_DURATION_MIN, " trip over 4 hours")

        # distance outliers
    flag(df, df["trip_distance"] <= 0, "zero or negative distance")
    flag(df,df["trip_distance"] > MAX_DISTANCE_MI, "distance over 100 miles")

        # impossible speed
    df["_speed_mph"] = df["trip_distance"] / (df["_duration_min"] / 60)
    flag(df, df["_speed_mph"] > MAX_SPEED_MPH, "speed over 80 mph")

        # money problems
    flag(df, df["fare_amount"] <= 0, "zero or negative fare")
    flag(df, df["total_amount"] <= 0, "zero or negative toatal")
    flag(df, (df[MONEY_COLUMNS].fillna(0) < 0).any(axis=1), "negative charge component")
    flag(df,df["fare_amount"] > MAX_FARE, "fare over $500")
    standard_rate = df["rate_code_id"] == 1
    flag(df, standard_rate & (df["fare_amount"] < MIN_FARE), "fare below $2.50 minimum")
    flag(df,df["tolls_amount"] > MAX_TOLLS, "tolls over $100")

        # invalid codes
    flag(df, ~df["rate_code_id"].isin(VALID_RATES_CODES), "invalid rate code")
    flag(df, ~df["payment_type"].isin(VALID_PAYMENT_TYPES), "invalid payment type")
    bad_zone = (~df["pu_location_id"].isin(valid_zone_ids) 
                | ~df["do_location_id"].isin(valid_zone_ids))
    flag(df, bad_zone, "unknown location ID")

        # too many passengers
    flag(df, df["passenger_count"] > MAX_PASSENGERS, "more than 6 passengers")

        # log and remove flagged rows
    bad = df["_reason"].notna()
    for reason, rows in df[bad].groupby("_reason"):
            logger.log(rows.drop(columns=HELPER_COLUMNS), reason, "excluded")
    clean = df[~bad].drop(columns=HELPER_COLUMNS).copy()

        # fix suspcious values
    no_pax = clean["passenger_count"].isna() | (clean["passenger_count"] == 0)
    logger.log(clean[no_pax], " 0 or missing passengers (set to 1)", "fixed")
    clean.loc[no_pax, "passenger_count"] = 1
    low_negotiated = (clean["rate_code_id"] == 5) & (clean["fare_amount"] < MIN_FARE)
    logger.log(clean[low_negotiated], "negotiated fare below $2.50", "suspicious")

        # congestion surchrage started feb 2019, so missing = no charge
    clean["congestion_surcharge"] = clean["congestion_surcharge"].fillna(0)

    clean["store_and_fwd_flag"] = (clean["store_and_fwd_flag"].fillna("N").astype(str).str.strip().str.upper())

        # standadize types
    for col in INT_COLUMNS:
            clean[col] = clean[col].astype("int16")
    clean[MONEY_COLUMNS] = clean[MONEY_COLUMNS].round(2) 
    return clean.reset_index(drop=True)   

if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    logger = RecordLogger() 

    trips = load_trips()
    zones = clean_zone_lookup(load_zone_lookup())
    total = len(trips)

    clean = clean_trips(trips, set(zones["location_id"]), logger)

    logger.print_summary(total)
    print(f"\n Clean rows : {len(clean):,}")
    print("\n Clean Column types:")
    print(clean.dtypes)
    print("\n Clean Numeric summary:")
    print(clean.describe().T)

    logger.save()

