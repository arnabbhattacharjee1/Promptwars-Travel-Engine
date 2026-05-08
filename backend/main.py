import os
from flask import Flask, request, jsonify, send_from_directory
from backend.agent import query_travel_engine

app = Flask(__name__)

# Directory for static files
static_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')

@app.route("/")
def index():
    return send_from_directory(static_dir, "index.html")

@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory(static_dir, path)

@app.route("/api/plan-travel", methods=["POST"])
def plan_travel():
    data = request.json
    plan = query_travel_engine(data)
    return jsonify(plan)

if __name__ == "__main__":
    # Get port from environment variable (default to 8000 for local testing)
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
