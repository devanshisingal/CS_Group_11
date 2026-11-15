# Web Server Security Assignment: OS Command Injection (Modular Structure)
**Course:** Cyber Security (IT-30001) - Autumn Semester 2026  

## Project Structure
```text
os_command_injection_modular/
│
├── app.py                      # Application entry point (Blueprints registry)
├── requirements.txt            # Python dependencies (Flask)
├── routes/
│   ├── inband_routes.py        # Variant 1: In-band routes (Vulnerable & Secure)
│   └── blind_routes.py         # Variant 2: Blind routes (Vulnerable & Secure)
├── templates/
│   └── index.html              # Frontend dashboard UI
└── README.md                   # Documentation & Ownership
```

## Setup & Running Instructions

### 1. Prerequisites
- Python 3.8 or higher installed on your system.
- *(Debian/Ubuntu only)* If `venv` is not already installed:
  ```bash
  sudo apt update && sudo apt install python3-venv python3-pip -y
  ```

### 2. Create a Virtual Environment (`venv`)
Using a Python virtual environment is strongly recommended to isolate dependencies and prevent package conflicts with system-managed Python packages.

From the project root directory (`OS-Command-Injection/`):

- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  ```
- **Windows:**
  ```cmd
  python -m venv venv
  ```

### 3. Activate the Virtual Environment
Before installing packages or running the app, activate the virtual environment:

- **Linux / macOS (Bash / Zsh):**
  ```bash
  source venv/bin/activate
  ```
- **Windows (Command Prompt):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  ```
  *(Note: If PowerShell displays a script execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

> **Tip:** You will know the virtual environment is active when `(venv)` appears at the start of your terminal prompt.

### 4. Install Dependencies
With the virtual environment activated, install the required dependencies:
```bash
pip install -r requirements.txt
```
*(Alternatively, you can install Flask directly with `pip install flask`)*

### 5. Run the Application
Start the Flask development server:
```bash
python app.py
```

### 6. Access the Application
Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

### 7. Deactivate the Virtual Environment (When Finished)
Once you are done testing, stop the server with `Ctrl + C`, then deactivate the virtual environment:
```bash
deactivate
```

---

## Demonstration & Testing Inputs (By Variant)

The web dashboard allows you to test both vulnerable and secured endpoints for each variant. Below are sample inputs and payloads for legitimate usage, attack demonstrations, and mitigation verification.

### Variant 1: In-Band / Direct OS Command Injection (Ping Tool)
In-band injection occurs when command output (`stdout` / `stderr`) is reflected directly back into the application response.

* **Endpoints:**
  * Vulnerable: `POST /inband` (uses string formatting with `shell=True`)
  * Mitigated / Secure: `POST /inband-secure` (uses regex validation and parameter list with `shell=False`)
* **Form Field:** `target`

#### 1. Legitimate Inputs (Normal Operation)
| Input Value | Description / Expected Behavior |
| :--- | :--- |
| `8.8.8.8` | Standard ping to Google Public DNS; returns ICMP packet transmission stats. |
| `127.0.0.1` | Local loopback ping; returns immediate ICMP echo replies. |
| `google.com` | Resolves domain and returns ping statistics. |

#### 2. Injection Payloads (Testing Vulnerable Route: `/inband`)
| Technique | Payload Example | Impact / Reflected Output |
| :--- | :--- | :--- |
| **Semicolon (`;`)** | `127.0.0.1; whoami` | Executes ping, then prints active OS user name (e.g. `user`). |
| **Semicolon (`;`)** | `127.0.0.1; id` | Prints system user ID, group ID, and group memberships. |
| **Semicolon (`;`)** | `127.0.0.1; uname -a` | Displays system kernel version and OS architecture. |
| **Semicolon (`;`)** | `127.0.0.1; ls -la` | Dumps current directory contents and file permissions. |
| **Semicolon (`;`)** | `127.0.0.1; cat /etc/passwd` | Discloses system user accounts list. |
| **Boolean AND (`&&`)** | `127.0.0.1 && whoami` | Executes second command only if ping succeeds. |
| **Boolean OR (`\|\|`)** | `invalid-host \|\| id` | Executes second command when initial ping fails. |
| **Pipe (`\|`)** | `127.0.0.1 \| uname -a` | Pipes output through shell command sequence. |
| **Subshell Expansion** | `$(whoami)` or `` `whoami` `` | Evaluates command substitution prior to argument parsing. |

#### 3. Mitigation Verification (Secure Route: `/inband-secure`)
* **Test Input:** Enter any malicious payload (e.g., `127.0.0.1; whoami` or `8.8.8.8 && id`).
* **Result:**
  ```text
  [BLOCKED] Invalid characters detected by input validation.
  ```
* **Mitigation Mechanism:** 
  1. Input is strictly validated using regex allow-list `^[a-zA-Z0-9.-]+$`. Metacharacters (`;`, `&`, `|`, `$`, spaces) are rejected.
  2. The command is invoked with `shell=False` and arguments passed as a distinct vector `['ping', '-c', '1', target]`, eliminating shell interpretation context.

---

### Variant 2: Blind / Indirect OS Command Injection (Lookup Tool)
In blind injection, command output is suppressed (`> /dev/null 2>&1`). Attackers cannot view command output in the HTTP response and must observe side-effects (such as time delays or file creation).

* **Endpoints:**
  * Vulnerable: `POST /blind` (uses `nslookup {domain} > /dev/null 2>&1` with `shell=True`)
  * Mitigated / Secure: `POST /blind-secure` (uses regex validation and native Python `socket.gethostbyname()`)
* **Form Field:** `domain`

#### 1. Legitimate Inputs (Normal Operation)
| Input Value | Endpoint | Expected Behavior |
| :--- | :--- | :--- |
| `google.com` | Vulnerable (`/blind`) | Immediate response: *"Lookup request processed (Blind: check response delay or logs)."* |
| `google.com` | Secure (`/blind-secure`) | Immediate response: *"Secure Native Lookup Successful. Resolved IP: 142.250.x.x"* |
| `example.com` | Both | Processes domain lookup immediately without delay. |

#### 2. Time-Based Injection Payloads (Testing Vulnerable Route: `/blind`)
*Observe wall-clock response time in your browser or developer network tab:*

| Technique | Payload Example | Impact / Expected Behavior |
| :--- | :--- | :--- |
| **Semicolon Delay** | `example.com; sleep 5` | HTTP response is delayed by **~5 seconds**, proving arbitrary command execution. |
| **Boolean AND Delay** | `example.com && sleep 7` | Causes a noticeable **7-second delay** before page renders. |
| **Boolean OR Delay** | `invalid-domain \|\| sleep 5` | Delays response if lookup fails. |
| **Subshell Delay** | `example.com; $(sleep 4)` | Triggers a **4-second sleep** via subshell evaluation. |

#### 3. Side-Effect / File-Based Verification Payloads (Testing Vulnerable Route: `/blind`)
*Verify arbitrary execution by inspecting server-side filesystem changes:*

| Payload Example | Verification in Terminal |
| :--- | :--- |
| `example.com; touch /tmp/blind_proof.txt` | Run `ls -l /tmp/blind_proof.txt` to confirm file creation. |
| `example.com; id > /tmp/blind_loot.txt` | Run `cat /tmp/blind_loot.txt` to inspect redirected command output. |

#### 4. Mitigation Verification (Secure Route: `/blind-secure`)
* **Test Input:** Enter `example.com; sleep 5` or `example.com && sleep 5`.
* **Result:**
  ```text
  [BLOCKED] Invalid domain format.
  ```
* **Mitigation Mechanism:**
  1. Input is validated with regex pattern `^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` to permit only standard domain syntax.
  2. Eliminates process invocation and shell execution entirely by utilizing Python's built-in networking API (`socket.gethostbyname(domain)`).

---

##  Ownership Declaration
| Member name | Roll number | Category | Variant implemented |
| :--- | :--- | :--- | :--- |
| Suvanwita Das | IIT2024013 | OS Command Injection | In-band & Blind |
