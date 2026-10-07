import sys
from pathlib import Path

import pandas as pd 

sys.path.append(str(Path(__file__).resolve().parent.parent))

from pipeline.load import load_trips, load_zone_lookup
from pipeline.clean import clean_trips, clean_zone_lookup
from pipeline.logger import RecordLogger

# Zone Ids for the three NYC airports (from taxi_zone_lookup.csv)
AIRPORT_ZONE_IDS={1, 132, 138} # Network (EWR), JFK, LaGuardia

TIME_OF_DAY_BINS =[0, 6, 10, 16, 20, 24]
TIME_OF_DAY_LABELS =["night", "morning_rush", "midday", "evening_rush", "evening"]

def add_features(df,zones):
    
 """ add derived features to the cleaned trips table."""
    
 df = df.copy()
 
 #1 trip duration in min
 df["trip_duration_min"] = ((df["dropoff_datetime"] -df ["pickup_datetime"]).dt.total_seconds() / 60 ).round(2)
 
  #2 average speed (mph): low speed = congestion
 df["avg_speed_mph"] = (df["trip_distance"] / (df["trip_duration_min"] / 60)).round(2)
 
 #3 fare per mile: show high price changes with trip length
 long_enough = df["trip_distance"] >= 0.5
 df["fare_per_mile"] = (df["fare_amount"] / df["trip_distance"]).round(2).where(long_enough)
 
 #4 trip percentage (card payment only: cash tips are not recorded) 
 is_card = df["payment_type"] == 1
 df["tip_pct"] = ((df["tip_amount"]/ df["fare_amount"]*100).round(2).where(is_card))
 
 #5 time features
 df["pickup_hour"] = df["pickup_datetime"].dt.hour.astype("int8")
 df["pickup_weekday"] = df["pickup_datetime"].dt.dayofweek.astype("int8") # 0 = monday
 df["is_weekend"] = df["pickup_weekday"]>=5
 df["time_of_day"] = pd.cut(df["pickup_hour"],bins=TIME_OF_DAY_BINS, labels=TIME_OF_DAY_LABELS, right=False).astype(str)
 
 #6 airport trips
 df["is_airport_trip"] = (df["pu_location_id"].isin(AIRPORT_ZONE_IDS) | df["do_location_id"].isin(AIRPORT_ZONE_IDS))
 
 #7 cross borough trips
 borough_of= zones.set_index("location_id")["borough"] 
 df["is_cross_borough"] = (df["pu_location_id"].map(borough_of) != df["do_location_id"].map(borough_of))
 
 return df

if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    logger = RecordLogger()
    
    zones = clean_zone_lookup(load_zone_lookup())
    trips = clean_trips(load_trips(), set(zones["location_id"]), logger) 
    trips = add_features(trips, zones)
    
    new_cols = ["trip_duration_min", "avg_speed_mph", "fare_per_mile", "tip_pct", "pickup_hour", "pickup_weekday", "is_weekend", "time_of_day", "is_airport_trip", "is_cross_borough"]
    
    print(f"Rows: {len(trips):,}")
    print("\nFirst 5 rows of new features:")
    print(trips[new_cols].head())
    print("\nNumeric summary of new features:")
    print(trips[new_cols].describe().T)
    print("\nTrips by time of day:")
    print(trips["time_of_day"].value_counts())
    print(f"\nAirport trips: {trips['is_airport_trip'].mean()*100:.1f}%")
    print(f"cross-borough trips: {trips['is_cross_borough'].mean()*100:.1f}%")
 
  