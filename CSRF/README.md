# SecureBank — CSRF Defense Lab

## Architecture and folder structure

SecureBank is a local FastAPI banking demo backed by SQLite and SQLAlchemy. The browser uses server-issued session cookies; transfers are implemented only as authenticated, token-checked POST requests. A GET request to `/transfer` is explicitly rejected with HTTP 405. The second local origin serves a read-only CSRF threat-model page; it does not send requests or change account state.

```text
CS-G11/
├── backend/
│   ├── main.py                 # FastAPI app factory, static pages, session middleware
│   ├── attacker_lab.py         # Read-only threat-model page on port 8001
│   ├── database.py             # SQLAlchemy engine, session factory, initial data
│   ├── models.py               # Account and Transaction tables
│   ├── schemas.py              # Validated API inputs
│   ├── auth.py                 # Password hashing, session auth, CSRF validation
│   ├── config.py               # Local paths and environment configuration
│   └── routers/
│       ├── authentication.py   # Login, logout, current identity
│       ├── accounts.py         # Balance and transaction history
│       └── secured.py          # GET rejection and secured POST transfer
├── frontend/
│   ├── login.html
│   ├── dashboard.html
│   ├── attacker.html           # Explanation only; no executable request
│   ├── css/style.css
│   └── js/app.js
├── tests/test_csrf.py
├── reset_db.py
├── run.py
├── video_script.readme
└── backend/requirements.txt
```

## Scope and safety

This project is a defensive, runnable CSRF lesson. It intentionally does **not** implement the requested auto-triggered forged cross-origin transfer or an exploitable state-changing GET route. That would make the project directly reusable as an unauthorized-transfer demonstration outside this lab. Instead, it demonstrates the concrete security property: the same GET URL shape returns 405 and leaves balances and transaction history unchanged.

The vulnerable design is described below as a threat model only. There is no vulnerable configuration switch and no vulnerable router in the executable app. The second-origin page is non-executable and read-only.

## What is CSRF?

Cross-Site Request Forgery (CSRF) is an attack in which a browser that is already authenticated to a site is induced to submit an unwanted request to that site. The browser may attach that site's cookies automatically. If an endpoint treats the presence of a valid session cookie as proof that the user intended the action, the server can mistake a forged request for a legitimate one.

### Request flow and root cause

1. A user logs into a site, and the browser holds a session cookie.
2. A malicious page causes the browser to request a state-changing URL at the authenticated site.
3. If the endpoint changes state on GET and relies only on the automatically attached session cookie, a visit or resource load can cause an action without the user's explicit intent.

The root cause is not merely “cookies are sent automatically.” It is the combination of ambient authentication and a state-changing endpoint that fails to establish request intent. GET is expected to be safe and should not perform transfers, purchases, deletion, or other state changes.

### Browser origins, sites, and SameSite

An **origin** includes scheme, host, and port. Thus `http://localhost:8000` and `http://localhost:8001` are different origins. “Same-site” is a different browser concept; different ports alone do not necessarily make sites cross-site. `localhost` and `127.0.0.1` are distinct hosts and are not interchangeable for host-only cookies.

Cookie sending also depends on cookie attributes and the request context. `SameSite=Lax` generally withholds cookies from cross-site subresource requests, while allowing some top-level safe navigations. `SameSite=Strict` is more restrictive. `SameSite=None` permits cross-site cookie use only with `Secure`, which normally requires HTTPS. Browser policies and localhost handling can vary. SameSite is useful defense-in-depth, but should not replace server-side CSRF validation for sensitive actions.

This app sets an HttpOnly, SameSite=Lax session cookie for local HTTP demonstration. The lab threat-model page does not attempt a request, so its outcome does not depend on browser cookie quirks.

## Implemented protections

1. **Avoid state-changing GET requests:** `GET /transfer` responds 405 with `Allow: POST`. It never authenticates and mutates an account as a side effect.
2. **Legitimate transfers use POST:** the transfer accepts a JSON body, requires a valid logged-in account, checks the recipient and amount, enforces available balance, and records the transaction atomically in the SQLAlchemy session.
3. **Synchronizer-style CSRF token:** login creates a random token stored in the signed session cookie. The client must send it in `X-CSRF-Token` for state-changing POST requests, including transfers and logout. The cookie is HttpOnly, so JavaScript cannot read it; the token is returned separately after successful login/current-user lookup.
4. **Other controls:** passwords are stored as salted PBKDF2 hashes; amounts are represented in integer paise; unsupported or invalid requests fail with explicit HTTP errors.

Changing GET to POST **alone is not complete CSRF protection**: HTML forms can issue cross-origin POST requests. This demo additionally validates a session-bound token. Production systems also need HTTPS, strong secret management, appropriate cookie settings, careful origin policy, and review of all state-changing routes.

### Demo accounts

| Username | Password | Initial balance |
|---|---|---:|
| alice | `password123` | ₹10,000.00 |
| attacker | `attacker123` | ₹0.00 |

Initial accounts are created on startup when the SQLite database is empty. The database is `securebank.db` in the project root by default.

## API and endpoint behavior

- `POST /api/auth/login` — authenticate and establish the session; returns a CSRF token.
- `POST /api/auth/logout` — clear session.
- `GET /api/auth/me` — current account and its CSRF token.
- `GET /api/account` — balance in integer paise.
- `GET /api/transactions` — account history.
- `GET /transfer?...` — always 405; no state change.
- `POST /transfer` — validated, CSRF-token-protected transfer.

An executable vulnerable endpoint would read `to` and `amount` from a GET query, identify the sender from the session cookie, and mutate balances without validating intent. That implementation is deliberately absent. The endpoint contract exercised by this project is the safe one: the same GET attempt is denied with 405, while a legitimate POST changes balances only when authenticated, well-formed, affordable, and accompanied by the token.
