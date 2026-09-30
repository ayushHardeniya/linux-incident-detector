import json
import subprocess
from datetime import datetime

WATCHED_FILE = "/etc/ssh/sshd_config"


def capture_context_snapshot():
    timestamp = datetime.now().isoformat()

    commands = {
        "PS": ["ps", "aux"],
        "SS": ["ss", "-tulpn"],
        "JOURNALCTL": ["journalctl", "--no-pager", "-n", "50"],
        "LAST": ["last", "-n", "10"],
    }

    snapshot = [
        "=== CONTEXT SNAPSHOT ===",
        f"Timestamp: {timestamp}",
    ]

    for name, command in commands.items():
        snapshot.append(f"\n=== {name} ===")

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

        snapshot.append(result.stdout)

        if result.stderr:
            snapshot.append(result.stderr)

    return "\n".join(snapshot)


def detect_event(file_path, event):
    return file_path == WATCHED_FILE and event == "MODIFY"

def save_finding(file_path, event_type, timestamp):
    findings_path = "runtime/findings.json"

    try:
        with open(findings_path) as f:
            findings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        findings = []

    finding = {
        "time": timestamp,
        "summary": f"{file_path} modified",
        "severity": "High",
    }

    findings.append(finding)

    with open(findings_path, "w") as f:
        json.dump(findings[-50:], f, indent=2)

def main():
    print("=== Linux Incident Detector ===")
    print("Watching:", WATCHED_FILE)

    for line in iter(input, ""):
        line = line.strip()

        if not line:
            continue

        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            print("Invalid event:", line)
            continue

        file_path = event.get("path")
        event_type = event.get("event")

        print(f"Event received: {file_path} [{event_type}]")

        if detect_event(file_path, event_type):
            print("INCIDENT DETECTED")

            snapshot = capture_context_snapshot()

            with open("evidence/day3_incident.txt", "w") as evidence:
                evidence.write("=== INCIDENT ===\n")
                evidence.write(f"File: {file_path}\n")
                evidence.write(f"Event: {event_type}\n")
                evidence.write(f"Agent timestamp: {event.get('timestamp')}\n\n")
                evidence.write(snapshot)

            save_finding(
                file_path,
                event_type,
                event.get("timestamp", datetime.now().isoformat()),
            )

            print("Context snapshot: ATTACHED")
            print("Evidence: evidence/day3_incident.txt")
        else:
            print("No incident")


if __name__ == "__main__":
    main()