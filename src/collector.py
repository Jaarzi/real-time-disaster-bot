# src/collector.py
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/metrics", methods=["POST"])
def metrics():
    data = request.get_json(force=True)
    app.logger.info("Received metrics: %s", data)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
