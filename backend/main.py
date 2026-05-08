import os
import logging
from flask import Flask, request, jsonify, send_from_directory, abort
from backend.agent import query_travel_engine

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security: Limit request body size to 1MB to prevent memory exhaustion attacks
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

# Directory for static files
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

@app.route("/")
def index():
    """Serve the main index.html safely."""
    try:
        return send_from_directory(STATIC_DIR, "index.html")
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        abort(404)

@app.route("/static/<path:path>")
def send_static(path):
    """Serve static assets safely using send_from_directory which prevents traversal."""
    return send_from_directory(STATIC_DIR, path)

@app.route("/api/plan-travel", methods=["POST"])
def plan_travel():
    """
    Main API endpoint for travel planning.
    Includes validation and safe error handling.
    """
    if not request.is_json:
        return jsonify({"error": "Bad Request", "message": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad Request", "message": "Empty payload"}), 400

    try:
        plan = query_travel_engine(data)
        return jsonify(plan)
    except Exception as e:
        logger.error(f"Unexpected error in plan_travel: {e}")
        # Secure: Do not expose stack trace to user
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "Payload Too Large", "message": "The request body exceeds the limit."}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found", "message": "The requested resource was not found."}), 404

if __name__ == "__main__":
    # Get port from environment variable (standard for Cloud Run)
    port = int(os.environ.get("PORT", 8000))
    # Production note: In deployment, use Gunicorn as configured in Dockerfile
    app.run(host="0.0.0.0", port=port, debug=False)
