# CS Group 11 

## Team

| Member | Roll Number | Lab |
|--------|-------------|-----|
| Devanshi Singal | IIT2024029 | XSS (Stored XSS) |
| Vaidik Kathal | IIT2024005  | CSRF Exploit & Defense |
| Kshitij Chatap | IIT2024004 | SQL Injection |
| Utkarsh Singh | IIT202052 | CSRF exploit (POST variant) |
| Suvanwita Das | IIT2024013 | OS Command Injection |

---
## Repository Structure

```
CS_Group_11/
│
├── CSRF/                        # Cross-Site Request Forgery Defense Lab
│   ├── backend/                 # FastAPI app (Python)
│   ├── frontend/                # HTML/CSS/JS frontend
│   ├── tests/                   # Pytest test suite
│   ├── run.py                   # Entry point
│   ├── reset_db.py              # Reset SQLite database
│   └── README.md
│
├── XSS/                         # Stored XSS Demo (Node/Express)
│   ├── server.js                # Express app (vulnerable + secure routes)
│   ├── listener.js              # Cookie theft listener
│   ├── db.json                  # In-memory comment store
│   ├── package.json
│   └── README.md
│
├── SQL_Injection/               # SQL Injection Auth Bypass (C++/MySQL)
│   ├── src/                     # C++ source files
│   ├── include/                 # Header files
│   ├── public/                  # Frontend (HTML/CSS/JS)
│   ├── database/                # SQL schema
│   ├── third_party/             # httplib.h
│   ├── Makefile
│   └── README.md
│
└── README.md                    # This file
```

---

## Labs Overview

### 🔐 CSRF — Cross-Site Request Forgery Defense
**Directory:** [`CSRF/`](./CSRF/)  
**Stack:** Python, FastAPI, SQLite, SQLAlchemy  
**What it demonstrates:**
- Why state-changing GET endpoints are dangerous
- How synchronizer-style CSRF tokens protect POST endpoints
- A live banking demo (SecureBank) with two accounts and a threat-model attacker page

**Quick start:**
```bash
cd CSRF
pip install -r backend/requirements.txt
python run.py
# Visit http://localhost:8000
```

---

### 🖥️ XSS — Stored Cross-Site Scripting Demo
**Directory:** [`XSS/`](./XSS/)  
**Stack:** Node.js, Express  
**What it demonstrates:**
- How stored XSS allows injected scripts to persist and run for every visitor
- Cookie theft via a malicious payload sent to a listener server
- Context-aware HTML output encoding as the mitigation

**Quick start:**
```bash
cd XSS
npm install
node server.js    # http://localhost:3000
node listener.js  # http://localhost:9000  (cookie theft listener)
```

---

### 🗄️ SQL Injection — Authentication Bypass Demo
**Directory:** [`SQL_Injection/`](./SQL_Injection/)  
**Stack:** C++17, MySQL, httplib  
**What it demonstrates:**
- Classic SQL injection authentication bypass (`' OR '1'='1' #`)
- Parameterized queries as the mitigation

**Quick start:**
```bash
cd SQL_Injection
make
export DB_HOST=127.0.0.1 DB_PORT=3306 DB_USER=root DB_PASSWORD="YOUR_PASSWORD"
./sql_injection_lab
# Visit http://127.0.0.1:8080
```

---

### 🖥️ OS Command Injection — Demo
**Directory:** [`OS_Command_Injection/`](./OS_Command_Injection/)  
**Stack:** Python, Flask  
**What it demonstrates:**
- How OS command injection can be exploited to execute arbitrary commands on the server
- Input validation and sanitization as the mitigation

**Quick start:**
```bash
cd OS_Command_Injection
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000
```

---

> All labs are for **educational use on localhost only**.
