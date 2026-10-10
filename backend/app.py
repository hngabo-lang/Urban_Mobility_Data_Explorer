from flask import Flask, jsonify
from flask_cors import CORS
from api.zones import zones_bp

def create_app():
    app = Flask(__name__)
    CORS(app) # allow the frontend (a different address) to call this API
    
    app.register_blueprint(zones_bp)
    
    @app.route("/api/health")
    def health():
        return jsonify({"status":"ok"})
    return app

app = create_app()
 
if __name__ == "__main__":
    app.run(debug=True, port=5000)
    
