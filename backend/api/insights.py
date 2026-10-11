from flask import Blueprint, jsonify, request
from database.db import query_all
from algorithms.custom_algo import top_k

insights_bp = Blueprint("insights", __name__, url_prefix="/api/insights")

DEFAULT_TOP_ZONES = 10
MAX_TOP_ZONES = 50

@insights_bp.route("/summary")
def summary():
    rows = query_all("""
        SELECT COUNT(*)                                  AS total_trips,
               ROUND(AVG(fare_amount), 2)                AS avg_fare,
               ROUND(AVG(trip_distance), 2)              AS avg_distance,
               ROUND(AVG(trip_duration_min), 2)          AS avg_duration_min,
               ROUND(AVG(avg_speed_mph), 2)              AS avg_speed_mph,
               ROUND(100.0 * AVG(is_airport_trip), 1)    AS airport_share_pct,
               ROUND(100.0 * AVG(is_cross_borough), 1)   AS cross_borough_share_pct
        FROM trips
    """)
    return jsonify(rows[0])

# summaries, hourly, weekly
@insights_bp.route("/hourly")
def hourly():
    rows = query_all    ("""
        SELECT pickup_hour                     AS hour,
               COUNT(*)                        AS trips,
               ROUND(AVG(avg_speed_mph), 2)    AS avg_speed_mph,
               ROUND(AVG(fare_amount), 2)      AS avg_fare
        FROM trips
        GROUP BY pickup_hour
        ORDER BY pickup_hour
    """)
    return jsonify(rows)

@insights_bp.route("/weekday")
def weekday():
    rows = query_all("""
        SELECT pickup_weekday AS weekday,
               COUNT(*)       AS trips
        FROM trips
        GROUP BY pickup_weekday
        ORDER BY pickup_weekday
    """)
    return jsonify(rows)

# zones and payments
@insights_bp.route("/top-zones")
def top_zones():
    try:
        limit = int(request.args.get("limit", DEFAULT_TOP_ZONES))
    except ValueError:
        return jsonify({"error": "'limit' must be a number"}), 400
    if limit < 1:
        return jsonify({"error": "'limit' must be 1 or more"}), 400
    limit = min(limit, MAX_TOP_ZONES)

    rows = query_all("""
        SELECT z.location_id, z.zone_name, b.borough_name,
               COUNT(*) AS trips
        FROM trips t
        JOIN zones z    ON z.location_id = t.pu_location_id
        JOIN boroughs b ON b.borough_id = z.borough_id
        GROUP BY z.location_id
    """)
    return jsonify(top_k(rows, limit, key=lambda r: r["trips"]))

@insights_bp.route("/zone-activity")
def zone_activity():
    rows = query_all("""
        SELECT pu_location_id AS location_id,
               COUNT(*)       AS pickups
        FROM trips
        GROUP BY pu_location_id
    """)
    return jsonify(rows)

@insights_bp.route("/payment")
def payment():
    rows = query_all("""
        SELECT p.description            AS payment_type,
               COUNT(*)                 AS trips,
               ROUND(AVG(t.tip_pct), 2) AS avg_tip_pct
        FROM trips t
        JOIN payment_types p ON p.payment_type_id = t.payment_type_id
        GROUP BY p.payment_type_id
        ORDER BY trips DESC
    """)
    return jsonify(rows)

