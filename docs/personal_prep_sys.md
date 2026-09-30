### expected path

```text

Linux Internals
      ↓
Processes & Filesystems
      ↓
System Calls / Kernel Interfaces
      ↓
Events & IPC
      ↓
Networking
      ↓
Concurrency
      ↓
Backend Systems
      ↓
Observability
      ↓
Reliability
      ↓
Distributed Systems
```

### topics to be learned during this project [linux-incident-detector]

| Phase  | Systems topic             | Why                                                |
| ------ | ------------------------- | -------------------------------------------------- |
| **1**  | `/proc` & `/sys`          | Understand how Linux exposes kernel/system state   |
| **2**  | Processes & PIDs          | Monitor processes and understand process lifecycle |
| **3**  | Filesystems & permissions | Detect configuration/file changes                  |
| **4**  | Linux logs & `journald`   | Detect authentication/system events                |
| **5**  | Signals & process control | Understand process events and graceful shutdown    |
| **6**  | System calls              | Understand what our programs actually invoke       |
| **7**  | `inotify`                 | Detect filesystem events                           |
| **8**  | Sockets & HTTP            | Go agent → Python backend communication            |
| **9**  | IPC                       | Understand alternatives to network communication   |
| **10** | Concurrency               | Go goroutines/channels + event processing          |
| **11** | Databases                 | Persist events/incidents correctly                 |
| **12** | Backend architecture      | API, workers, queues, state                        |
| **13** | Observability             | Metrics, logs, health, debugging                   |
| **14** | Reliability               | retries, failure handling, buffering               |
| **15** | Distributed systems       | Later expansion to multiple Linux hosts            |


## Attack

```text
ATTACK
  ↓
Modify /etc/ssh/sshd_config
  ↓
echo "PermitRootLogin yes" | sudo tee -a /etc/ssh/sshd_config
  ↓
LINUX FILESYSTEM
  ↓
inotify detects filesystem event
  ↓
OPEN → MODIFY → CLOSE_WRITE,CLOSE
  ↓
SNAPSHOT
  ├── ps
  ├── ss
  ├── journalctl
  └── last
  ↓
config-tampering.txt

```

