# Urban_Mobility_Data_Explorer

A fullstack application built on real world data: the NYC taxi and Limousine commision's **january 2019 yellow taxi trips** (7.6 million records). The raw data is cleaned with python pipeline, stored in a normalised **SQLITE** database, served by a **flask** API, and explored in an interactive **HTML/CSS/JS** dashboard with filtering, sorting and paging.

- **Video Walkthrough:** (https://youtu.be/okYcFL6v8MA?si=4Hh8U3LwIQL9uLqA)

- **Team members/authors:** -Griphen Mweene,
                            -Aristote Henry Ngabo,
                            -Precious Amarachi Azubuike.

- **Team task sheet:** [Google Sheet](https://docs.google.com/spreadsheets/d/1I0N5eUctzWSUkwSLzQiU75zSHnxQZl7PzwDWK2OGUro/edit?usp=sharing)
- **Technical_report:** [docs/technical_report.pdf](docs/technical_report.pdf)

## Features
-**Derived features.** Trip duration, average speed, fare per mile, tip %, time of day, airport trip and cross-borough trip.

-**Normalised database** 7 tables with foreign keys, CHECK constaints and 8 indexes.

-**REST API.** 12 endpoints for trips, zones and insights. All queries use parameterised SQL.

-**Dashboard.**
 - 7 summary cards.
 -4 charts, each with a sentence explaining the insight.
 page through, with a popup showing each trip's details.
 
 ```
 ## Project structure
 ```
Urban_Mobility_Data_Explorer/
├── backend/
│   ├── app.py              # Flask app, registers the API blueprints
│   ├── config.py           # all file paths and settings
│   ├── requirements.txt
│   ├── api/                # zones.py, trips.py, insights.py
│   ├── pipeline/           # load.py, clean.py, features.py, logger.py, run_pipeline.py
│   ├── database/           # schema.sql, db.py, insert.py
│   └── algorithms/         # custom_algo.py (MinHeap + top_k)
├── frontend/
│   ├── index.html
│   ├── css/styles.css
│   └── js/                 # api.js, filters.js, charts.js, map.js, main.js
├── data/raw/               # raw TLC files (not in git, see below)
├── logs/                   # excluded/fixed/suspicious records log
└── docs/                   # technical report, cleaning summary

## Setup

###1. clone and create a virtual environment

```bash
git clone https://github.com/hngabo-lang/Urban_Mobility_Data_Explorer.git

python -m venv venv 
source venv/bin/activate        # windows (git bash)
# venv\scripts\Avtivate.ps1     # Windows (powershell)
# sourse venv/bin/activate      # macOS / Linux

pip install -r backend/requirements.txt
```

### 2. Download the raw data

the data files are to0 large for Github, so download then from the [NYC TLC Trip Record data] (https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) page and put them in `data/raw/` :

| File | Description |
|---|---|
| `yellow_tripdata_2019-01.csv` | January 2019 yellow taxi trips (~648 MB) |
| `taxi_zone_lookup.csv` | Zone ID → zone name and borough |
| `taxi_zones.shp` (+ `.shx`, `.dbf`, `.prj`) | Zone boundaries (keep all the shapefile parts together) |

### 3. Build the database

```bash
cd  backend
python pipeline/run_pipeline.py
```

this laods, cleans and enriches the trip, then creates
`backend/database/mobility_data.db`. It takes **about 5-6 minutes** on the full month. to test faster, set
`SAMPLE_ROWS = 500_000` in `config.py`.

### 4. start the backend

```bash
# still inside backend/
python app.py
```

The API runs at `http://127.0.0.1:5000`. Check it with
`http://127.0.0.1:5000/api/health`, wich should return `{"status": "ok"}`.

### 5. open the dashboard

In a **second terminal**:

```bash
cd frontend
python -m http.server 8000
```

then open `hhtp://localhost:8000` in your browser. Keep the backend running while you use the dashboard.

---

## API endpoints

| Endpoint | Returns |
|---|---|
| `GET /api/health` | Health check |
| `GET /api/boroughs` | List of boroughs |
| `GET /api/zones` | 265 zones with borough names |
| `GET /api/zones/geojson` | Zone polygons for the map |
| `GET /api/trips` | Trips, with filters, sorting and paging |
| `GET /api/trips/<id>` | One trip with all its details |
| `GET /api/insights/summary` | Headline statistics |
| `GET /api/insights/hourly` | Trips and average speed per hour |
| `GET /api/insights/weekday` | Trips per day of the week |
| `GET /api/insights/top-zones?limit=10` | Busiest zones, ranked by our `top_k` algorithm |
| `GET /api/insights/zone-activity` | Pickups per zone, for the map |
| `GET /api/insights/payment` | Trips and average tip % per payment type |

**`/api/trips` filters:** ``start_date`, `end_date`,
`hour`, `time_of_day`, `borough`, `min_distance`, `max_distance`, `min_fare`, `max_fare`, `payment_type`, `airport`.
**sorting:** `sort`, `order` (`asc`/`desc`). **paging:**
`page`, `page_size` (max 100)

example: `/api/trips?borough=Manhattan&min_fare=20&sort=fare_amount&order=desc`

---

## data cleaning summary

| | Trips | share |
|---|---|---|
| Raw records| 7,667,792 | 100% |
| **keep after cleaning** | **7,555,473** | **98.54%** |
| Excluded | 112,319 | 1.46% |
| Fixed (0 passengers → 1) |114,741 | kept |
| suspicious (flagged, kept) | 310 | kept |

The mainexclusion rules were trips under 1 minute, trips over 4 hours, zero distance, dropoff not after pickup and zero fare. The full output is in [docs/cleaning_output.txt](docs/cleaning_output.txt).

Running the pipeline creates the full record log at `logs/excluding_records.csv`. that file is too large for github, so the repo includes a 1,000-row sample instead: [logs/excluded_records_sample.csv](logs/excluded_records_sample.csv).

---

## Tech stack

| Layer| Technology |
|---|---|
| Data pipeline | python, pandas, geopanda |
| database | SQLite |
| Backend | Flask, flask-cors |
| Frontend | HTML, CSS, Javascript, Chart.js, Leaflet (OpenStreetMap title) |

---



