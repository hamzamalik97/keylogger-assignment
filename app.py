from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)
RECEIVER = "http://127.0.0.1:5002"

PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Keyboard Event Lab</title>
<style>
body {font:15px/1.5 system-ui,sans-serif;max-width:1100px;margin:32px auto;padding:0 16px}
.notice {background:#eef3f8;color:#17212b;padding:12px;border-radius:8px}
textarea {width:100%;min-height:115px;box-sizing:border-box;padding:12px;font:inherit}
.controls {display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}
input[type=search] {flex:1;min-width:220px;padding:10px;font:inherit}
button {padding:9px 13px;cursor:pointer}
.table-wrap {overflow-x:auto}
table {width:100%;border-collapse:collapse;margin-top:10px}
th,td {border-bottom:1px solid #8886;padding:9px;text-align:left;vertical-align:top}
th {white-space:nowrap}
td.text {white-space:pre-wrap;overflow-wrap:anywhere;min-width:180px}
.small {opacity:.75;font-size:13px}
</style>
</head>
<body>
<h1>Keyboard Event Lab</h1>
<div class="notice"><strong>Controlled test only.</strong>
Events are recorded only from this test field. Use sample text, never passwords
or personal information.</div>

<h2>Test input</h2>
<p>Type sample text below. Key events and updated text snapshots are sent to the receiver.</p>
<textarea id="testInput" placeholder="Type sample text here..."></textarea>
<p id="status">Waiting for input.</p>

<h2>Stored events</h2>
<div class="controls">
<input id="search" type="search"
 placeholder="Search source, timestamp, event type, key, or text...">
<button id="refresh" type="button">Refresh events</button>
<button id="clear" type="button">Clear search</button>
</div>
<div id="summary" class="small">Loading events...</div>
<div class="table-wrap">
<table>
<thead><tr><th>Received at (UTC)</th><th>Event type</th>
<th>Source</th><th>Key</th><th>Text / command</th><th>Sequence</th><th>Exit status</th></tr></thead>
<tbody id="eventRows"></tbody>
</table>
</div>

<script>
const field = document.getElementById("testInput");
const statusBox = document.getElementById("status");
const searchBox = document.getElementById("search");
const rows = document.getElementById("eventRows");
const summary = document.getElementById("summary");
let sequence = 0;
let queue = Promise.resolve();
let allEvents = [];

function sendEvent(type, key, text) {
  const event = {
    source: "browser",
    event_type: type,
    key: key || "",
    text: text || "",
    sequence: ++sequence
  };

  queue = queue.then(async () => {
    const response = await fetch("/record", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(event)
    });
    if (!response.ok) throw new Error("Recording failed");
    statusBox.textContent =
      "Receiver stored event " + event.sequence + " (" + event.event_type + ")";
    await loadEvents();
  }).catch(() => {
    statusBox.textContent = "Recording failed. Check that the receiver is running.";
  });
}

function cell(row, value) {
  const td = document.createElement("td");
  td.textContent = value == null ? "" : String(value);
  row.appendChild(td);
}

function renderEvents() {
  const term = searchBox.value.trim().toLowerCase();
  const filtered = allEvents.filter(event =>
    [event.source, event.received_at, event.event_type, event.key, event.text, event.sequence, event.exit_status]
      .some(value => String(value ?? "").toLowerCase().includes(term))
  );

  rows.replaceChildren();

  if (!filtered.length) {
    const row = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 7;
    td.textContent = allEvents.length
      ? "No events match this search."
      : "No stored events yet.";
    row.appendChild(td);
    rows.appendChild(row);
  } else {
    for (const event of filtered.slice().reverse()) {
      const row = document.createElement("tr");
      cell(row, event.received_at || "");
      cell(row, event.event_type || "");
      cell(row, event.source || "unknown");
      cell(row, event.key || "");
      const textCell = document.createElement("td");
      textCell.className = "text";
      textCell.textContent = event.text || "";
      row.appendChild(textCell);
      cell(row, event.sequence ?? "");
      cell(row, event.exit_status ?? "—");
      rows.appendChild(row);
    }
  }
  summary.textContent =
    "Showing " + filtered.length + " of " + allEvents.length + " retrieved events.";
}

async function loadEvents() {
  try {
    const response = await fetch("/events", {cache: "no-store"});
    if (!response.ok) throw new Error("Fetch failed");
    const data = await response.json();
    allEvents = Array.isArray(data.events) ? data.events : [];
    renderEvents();
  } catch {
    summary.textContent = "Cannot retrieve events. Check the receiver and application.";
  }
}

field.addEventListener("keydown", event =>
  sendEvent("key_down", event.key, ""));
field.addEventListener("input", () =>
  sendEvent("text_snapshot", "", field.value));
searchBox.addEventListener("input", renderEvents);
document.getElementById("refresh").addEventListener("click", loadEvents);
document.getElementById("clear").addEventListener("click", () => {
  searchBox.value = "";
  renderEvents();
  searchBox.focus();
});
loadEvents();
</script>
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(PAGE)

@app.post("/record")
def record():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Expected JSON"), 400
    try:
        response = requests.post(RECEIVER + "/events", json=data, timeout=3)
        return response.text, response.status_code, {
            "Content-Type": "application/json"
        }
    except requests.RequestException:
        return jsonify(error="Receiver unavailable"), 502

@app.get("/events")
def events():
    try:
        response = requests.get(RECEIVER + "/events", timeout=3)
        return response.text, response.status_code, {
            "Content-Type": "application/json"
        }
    except requests.RequestException:
        return jsonify(error="Receiver unavailable"), 502

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
