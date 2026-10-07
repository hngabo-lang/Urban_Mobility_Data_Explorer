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

