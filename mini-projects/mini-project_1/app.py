import json
import os
import shutil
import threading
from datetime import datetime

from flask import Flask, jsonify, render_template, request

from bots import generate_swarm

app = Flask(__name__)

DATA_FILE = "data/swarms.json"
SEED_FILE = "data/seed_swarms.json"
lock = threading.Lock()  # Flask can handle requests concurrently

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"swarms": []}

def save_data(data):
    # Write to a temp file, then swap it in, so a crash can't corrupt the JSON.
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, DATA_FILE)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/amplify", methods=["POST"])
def amplify():
    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text", "")).strip()

    if not text or len(text) > 200:
        return jsonify({"error": "Text must be 1-200 characters."}), 400

    with lock:
        data = load_data()
        swarm = {
            "id": f"swarm_{len(data['swarms']) + 1:03d}",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "original": {"text": text, "handle": "user_you"},
            "bots": generate_swarm(text),
        }
        data["swarms"].append(swarm)
        save_data(data)

    return jsonify(swarm)

@app.route("/api/swarms", methods=["GET"])
def swarms():
    with lock:
        return jsonify(load_data())

@app.route("/api/reset", methods=["POST"])
def reset():
    with lock:
        shutil.copy(SEED_FILE, DATA_FILE)
    return jsonify({"ok": True})

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        if os.path.exists(SEED_FILE):
            shutil.copy(SEED_FILE, DATA_FILE)
    app.run(debug=True)