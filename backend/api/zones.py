import json
from flask import Blueprint, jsonify
from database.db import query_all
zones_bp = Blueprint("zones",__name__,url_prefix="/api")

@zones_bp.route("/boroughs")
def list_boroughs():
    rows = query_all(
    "SELECT borough_id, borough_name FROM boroughs ORDER BY borough_name")
    
    return jsonify(rows)

@zones_bp.route("/zones")
def list_zones():
    rows = query_all("""
                     SELECT z.location_id,z.zone_name,b.borough_name,z.service_zone
                     FROM zones z JOIN boroughs b ON b.borough_id = z.borough_id
                     ORDER BY z.location_id
                     """)
    return jsonify(rows)

@zones_bp.route("/zones/geojson")
def zones_geojson():
    """
    All zone polygons are one GeoJSON FeatureCollection for the map.
    """
    rows = query_all(
        """ SELECT s.location_id, s.geojson, z.zone_name, b.borough_name 
        FROM zone_shapes s JOIN zones z ON z.location_id = s.location_id
        JOIN boroughs b ON b.borough_id = z.borough_id
        """
    )
    features=[
        {
            "type":"Feature",
            "geometry":json.loads(row["geojson"]),
            "properties":{
                "location_id":row["location_id"],
                "zone":row["zone_name"],
                "borough":row["borough_name"],
            },
        }
        for row in rows
    ]
    return jsonify({"type":"FeatureCollection", "features":features})
                       
                        
            
                
    