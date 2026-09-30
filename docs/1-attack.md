# P_206 — Incident Detection on Linux Server

## Documentation — Config Tampering Test [Attack]

### 1. What was the task?

We needed to demonstrate one complete incident-detection flow:

> **Detect an unauthorized change to a critical Linux configuration file and capture the system state around that incident.**

We used:

```text
/etc/ssh/sshd_config
```

as the monitored configuration file.

The specific test was:

```text
Modify sshd_config
       ↓
inotify detects file change
       ↓
Collect evidence
       ↓
Create Context Snapshot
       ↓
Save evidence for the incident
```

---

## 2. What we actually did

### Step 1 — Prepared the Ubuntu VM

Created a separate **Ubuntu 24.04 VirtualBox VM**:

```text
Host Windows
     │
     ▼
VirtualBox
     │
     ▼
Ubuntu 24.04 VM
     │
     └── ubuntu-vm
```

This is our controlled Linux server where we can safely generate suspicious activity.

We also created a clean snapshot:

```text
Clean Ubuntu 24.04 - Before Incident Test
```

This lets us restore the VM to its original state later.

---

### Step 2 — Installed `inotify-tools`

```bash
sudo apt install -y inotify-tools
```

Purpose:

> Allows us to monitor filesystem changes.

Verified:

```bash
which inotifywait
```

---

### Step 3 — Installed SSH server

Initially `/etc/ssh/sshd_config` did not exist, so we installed OpenSSH:

```bash
sudo apt install -y openssh-server
```

Then verified:

```bash
ls -l /etc/ssh/sshd_config
```

---

# 3. Started the file watcher

We monitored the SSH configuration file using:

```bash
sudo inotifywait -m /etc/ssh/sshd_config
```

`-m` means:

> Keep monitoring instead of exiting after the first event.

Output:

```text
Setting up watches.
Watches established.
```

Then when the file was changed, we saw:

```text
/etc/ssh/sshd_config OPEN
/etc/ssh/sshd_config MODIFY
/etc/ssh/sshd_config CLOSE_WRITE,CLOSE
```

The important event was:

```text
MODIFY
```

This proves that the file-monitoring mechanism detected the configuration change.

---

# 4. Performed the controlled tampering

We modified the configuration:

```bash
sudo sed -i '/^PermitRootLogin yes$/d' /etc/ssh/sshd_config
```

and then injected:

```bash
echo "PermitRootLogin yes" | sudo tee -a /etc/ssh/sshd_config
```

The second command is the actual **tampering simulation**.

We verified it with:

```bash
tail -n 5 /etc/ssh/sshd_config
```

which showed:

```text
PermitRootLogin yes
```

So our test was:

```text
Attacker / unauthorized action
          │
          ▼
Modify /etc/ssh/sshd_config
          │
          ▼
inotifywait
          │
          ▼
MODIFY event
```

---

# 5. Created the Context Snapshot

We created:

```text
~/incident-evidence/config-tampering.txt
```

This is the important part of our project.

Instead of simply saying:

> "sshd_config was modified"

we captured the **state of the system around the incident**.

The file contains sections such as:

```text
=== INCIDENT: SSH CONFIG TAMPERING ===

=== AFFECTED FILE ===
/etc/ssh/sshd_config

=== MODIFIED CONFIG ===
...

=== PS ===
...

=== SS ===
...

=== JOURNALCTL ===
...

=== LAST ===
...
```

---

# 6. What each command in the snapshot does

### `date`

```bash
date
```

Records **when the incident/context snapshot was taken**.

---

### `hostname`

```bash
hostname
```

Records **which Linux machine** generated the evidence.

Example:

```text
ubuntu-vm
```

Useful when we eventually monitor multiple machines.

---

### Affected file

```bash
echo "/etc/ssh/sshd_config"
```

Simply records the file involved in the incident.

---

### Modified configuration

```bash
tail -n 5 /etc/ssh/sshd_config
```

Shows the relevant recent lines of the configuration.

In our case it showed:

```text
PermitRootLogin yes
```

This is direct evidence of the configuration change.

---

## `ps aux`

```bash
ps aux
```

Shows currently running processes.

Purpose:

> What processes were running when the incident happened?

This becomes useful for investigating whether a suspicious process was active.

---

## `ss -tulpn`

```bash
sudo ss -tulpn
```

Shows listening/network sockets.

Purpose:

> What network services/connections were active during the incident?

For example:

```text
tcp LISTEN ... :22
```

helps identify services listening on the machine.

---

## `journalctl`

```bash
sudo journalctl --no-pager -n 50
```

Shows the most recent 50 systemd journal entries.

Purpose:

> What system/authentication/service events happened around the incident?

This is especially useful because authentication and system events are recorded by `journald`.

---

## `last -n 10`

```bash
last -n 10
```

Shows recent login/session history.

Purpose:

> Who recently logged into the machine and when?

Example:

```text
ayush   tty2
ayush   seat0
reboot  system boot
```

---

# 7. Final evidence structure

Our evidence directory was:

```text
~/incident-evidence/
│
├── config-tampering.txt
│
├── config-tampering.png
│
└── [other proof/screenshots]
```

### `config-tampering.txt`

**Main evidence / Context Snapshot**

Contains:

```text
incident
   │
   ├── timestamp
   ├── hostname
   ├── affected file
   ├── modified configuration
   ├── running processes
   ├── network sockets
   ├── recent journal events
   └── recent login history
```

### `config-tampering.png`

**Visual proof**

Screenshot showing the terminal output / evidence of the tampering test.

Useful for:

* presentation
* project report
* demonstrating that the test actually happened

### inotify screenshot / proof

Shows:

```text
OPEN
MODIFY
CLOSE_WRITE,CLOSE
```

This is the proof that the **file-monitoring mechanism detected the modification**.

---

# 8. What did we actually prove?

The complete prototype flow we demonstrated is:

```text
                 Ubuntu 24.04 VM
                       │
                       │
              Modify sshd_config
                       │
                       ▼
              ┌─────────────────┐
              │    inotify      │
              │ File Monitoring │
              └────────┬────────┘
                       │
                  MODIFY event
                       │
                       ▼
              ┌─────────────────┐
              │    Evidence     │
              │    Collection   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Context Snapshot│
              ├─────────────────┤
              │ ps              │
              │ ss              │
              │ journalctl      │
              │ last            │
              │ config state    │
              └────────┬────────┘
                       │
                       ▼
             config-tampering.txt
```

### In project terminology

**Event:**

```text
/etc/ssh/sshd_config → MODIFY
```

**Incident:**

```text
SSH configuration tampering
```

**Context Snapshot:**

```text
File state + processes + network state
+ system logs + login history + timestamp
```

This is the core idea we wanted to demonstrate with the project: **don't just detect that something happened; capture the relevant system state at the time of the incident.**
