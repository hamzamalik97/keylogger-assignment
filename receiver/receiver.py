from flask import Flask, request, jsonify
from datetime import datetime, timezone
from pathlib import Path
import json

app = Flask(__name__)
log_file = Path("/logs/events.jsonl")
log_file.parent.mkdir(parents=True, exist_ok=True)

@app.get("/health")
def health():
    return jsonify(status="ok", service="lab-receiver")

@app.post("/events")
def receive():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Expected JSON"), 400

    record = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "source": str(data.get("source", "unknown"))[:40],
        "event_type": str(data.get("event_type", "input"))[:40],
        "key": str(data.get("key", ""))[:80],
        "text": str(data.get("text", ""))[:5000],
        "sequence": data.get("sequence")
    }

    if "exit_status" in data:
        try:
            record["exit_status"] = int(data["exit_status"])
        except (ValueError, TypeError):
            return jsonify(error="exit_status must be an integer"), 400

    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return jsonify(status="stored", received_at=record["received_at"]), 201

@app.get("/events")
def events():
    records = []
    if log_file.exists():
        with log_file.open(encoding="utf-8") as f:
            for line in f:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return jsonify(events=records[-200:])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
