
from datetime import datetime
from flask import Blueprint, jsonify, request
from database.db import query_all

trips_bp = Blueprint("trips" , __name__, url_prefix="/api")

# Columns users may sort

SORTABLE_COLUMNS = {
    "pickup_datetime": "t.pickup_datetime",
    "trip_distance": "t.trip_distance",
    "trip_duration_min": "t.trip_duration_min",
    "fare_amount": "t.fare_amount",
    "total_amount": "t.total_amount",
    "tip_pct": "t.tip_pct",
    "avg_speed_mph": "t.avg_speed_mph",
}
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100

# join shared by list and detail querry
BASE_FROM = """
    FROM trips t
    JOIN zones pu_zone    ON pu_zone.location_id = t.pu_location_id
    JOIN boroughs pu_boro ON pu_boro.borough_id = pu_zone.borough_id
    JOIN zones do_zone    ON do_zone.location_id = t.do_location_id
    JOIN boroughs do_boro ON do_boro.borough_id = do_zone.borough_id
"""

# read a number from a URL
def get_number(name, cast=float):
    value = request.args.get(name)
    if value is None or value == "":
        return None
    try:
        return cast(value)
    except ValueError:
        raise ValueError(f"'{name}' must be a number")

# read date from the URL
def get_date(name):
    value = request.args.get(name)
    if not value:
        return None
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"'{name}' must be a date like 2019-01-02")
    return value

#turn url parameters into a SQL WHERE clause and its value
def build_filters():
    conditions, params = [], []

    def add(sql, value):
        if value is not None:
            conditions.append(sql)
            params.append(value)

    end_date = get_date("end_date")
    add("t.pickup_datetime >= ?", get_date("start_date"))
    add("t.pickup_datetime <= ?", f"{end_date} 23:59:59" if end_date else None)
    add("t.pickup_hour = ?", get_number("hour", int))
    add("pu_boro.borough_name = ?", request.args.get("borough") or None)
    add("t.pu_location_id = ?", get_number("pickup_zone", int))
    add("t.do_location_id = ?", get_number("dropoff_zone", int))
    add("t.trip_distance >= ?", get_number("min_distance"))
    add("t.trip_distance <= ?", get_number("max_distance"))
    add("t.fare_amount >= ?", get_number("min_fare"))
    add("t.fare_amount <= ?", get_number("max_fare"))
    add("t.payment_type_id = ?", get_number("payment_type", int))
    add("t.time_of_day = ?", request.args.get("time_of_day") or None)
    add("t.is_airport_trip = ?", get_number("airport", int))

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return where, params

# paging and sorting
def get_paging():
    page = get_number("page", int) or 1
    size = get_number("page_size", int) or DEFAULT_PAGE_SIZE
    if page < 1 or size < 1:
        raise ValueError("'page' and 'page_size' must be 1 or more")
    return page, min(size, MAX_PAGE_SIZE)


def get_sort():
    sort = request.args.get("sort", "pickup_datetime")
    if sort not in SORTABLE_COLUMNS:
        raise ValueError(f"'sort' must be one of: {', '.join(SORTABLE_COLUMNS)}")
    order = request.args.get("order", "desc").lower()
    if order not in ("asc", "desc"):
        raise ValueError("'order' must be 'asc' or 'desc'")
    return f"{SORTABLE_COLUMNS[sort]} {order.upper()}"


# routes
@trips_bp.route("/trips")
def list_trips():
    try:
        where, params = build_filters()
        page, size = get_paging()
        order_by = get_sort()
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    total = query_all(f"SELECT COUNT(*) AS n {BASE_FROM} {where}", params)[0]["n"]

    rows = query_all(f"""
        SELECT t.trip_id, t.pickup_datetime, t.dropoff_datetime,
               pu_zone.zone_name AS pickup_zone, pu_boro.borough_name AS pickup_borough,
               do_zone.zone_name AS dropoff_zone, do_boro.borough_name AS dropoff_borough,
               t.trip_distance, t.trip_duration_min, t.fare_amount,
               t.tip_amount, t.total_amount, t.tip_pct
        {BASE_FROM}
        {where}
        ORDER BY {order_by}, t.trip_id
        LIMIT ? OFFSET ?
    """, params + [size, (page - 1) * size])
    return jsonify({
        "page": page,
        "page_size": size,
        "total": total,
        "total_pages": (total + size - 1) // size,
        "trips": rows,
    })

@trips_bp.route("/trips/<int:trip_id>")
def trip_detil(trip_id):
    rows = query_all(f"""
        SELECT t.*,
               pu_zone.zone_name AS pickup_zone, pu_boro.borough_name AS pickup_borough,
               do_zone.zone_name AS dropoff_zone, do_boro.borough_name AS dropoff_borough,
               v.vendor_name, r.description AS rate_code, p.description AS payment_type
        {BASE_FROM}
        JOIN vendors v       ON v.vendor_id = t.vendor_id
        JOIN rate_codes r    ON r.rate_code_id = t.rate_code_id
        JOIN payment_types p ON p.payment_type_id = t.payment_type_id
        WHERE t.trip_id = ?
    """, [trip_id]
    )
    if not rows:
        return jsonify({"error": f"Trip {trip_id} not found"}), 404
    return jsonify(rows[0])

    