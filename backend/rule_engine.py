import subprocess
from datetime import datetime

WATCHED_FILE = "/etc/ssh/sshd_config"
EVENT_FEED = "evidence/event_feed.txt"


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


def main():
    print("=== Linux Incident Detector ===")
    print("Watching:", WATCHED_FILE)

    with open(EVENT_FEED) as feed:
        for line in feed:
            line = line.strip()

            if not line:
                continue

            file_path, event = line.split("|", 1)

            print(f"Event received: {file_path} [{event}]")

            if detect_event(file_path, event):
                print("INCIDENT DETECTED")

                snapshot = capture_context_snapshot()

                with open("evidence/day3_incident.txt", "w") as evidence:
                    evidence.write("=== INCIDENT ===\n")
                    evidence.write(f"File: {file_path}\n")
                    evidence.write(f"Event: {event}\n\n")
                    evidence.write(snapshot)

                print("Context snapshot: ATTACHED")
                print("Evidence: evidence/day3_incident.txt")
            else:
                print("No incident")


if __name__ == "__main__":
    main()