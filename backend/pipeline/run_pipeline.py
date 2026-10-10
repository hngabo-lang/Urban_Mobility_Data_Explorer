import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from database.insert import populate_database


def main():
    sample = config.SAMPLE_ROWS
    print("=" * 50)
    print("NYC Taxi Mobility pipeline")
    print(f"Rows to load: {'ALL' if sample is None else f'{sample:,} (sample)'}")
    print("=" * 50)

    start = time.time()
    populate_database()
    minutes = (time.time() - start) / 60


    print("=" * 50)
    print(f"pipeline finished in {minutes:.1f} minutes")
    print("=" * 50)

if __name__ == "__main__":
    main()




    