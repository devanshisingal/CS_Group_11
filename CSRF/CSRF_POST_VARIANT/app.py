from flask import (
    Flask, request, session, redirect,
    url_for, render_template_string, abort
)
import secrets
import hmac

app = Flask(__name__)

app.secret_key = "replace-this-with-a-random-secret"

# Local demonstration configuration
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False
)

VICTIM_ORIGIN = "http://localhost:5000"


HOME = """
<!DOCTYPE html>
<html>
<head>
    <title>Demo Bank</title>
</head>
<body>
    <h1>Demo Bank</h1>

    {% if not session.get('logged_in') %}
        <p>You are not logged in.</p>
        <a href="/login">Login as Demo User</a>
    {% else %}
        <h3>Welcome, Demo User!</h3>

        <p>Account balance: {{ session.get('balance', 1000) }} points</p>

        <hr>

               <h2> Transfer</h2>

        <form action="/transfer-protected" method="POST">
            <input type="hidden" name="csrf_token"
                   value="{{ csrf_token }}">

            <label>Recipient:</label>
            <input name="recipient" value="Alice">

            <label>Amount:</label>
            <input name="amount" type="number" value="100">

            <button type="submit">Transfer (Protected)</button>
        </form>

        <hr>

        <a href="/logout">Logout</a>
    {% endif %}

    {% if message %}
        <h3>{{ message }}</h3>
    {% endif %}
</body>
</html>
"""


def authenticated():
    if not session.get("logged_in"):
        abort(401, "Please log in first.")


@app.route("/")
def home():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)

    return render_template_string(
        HOME,
        csrf_token=session["csrf_token"],
        message=request.args.get("message"),
        session=session
    )


@app.route("/login")
def login():
    # Simulated login for the demonstration.
    session.clear()

    session["logged_in"] = True
    session["balance"] = 1000
    session["csrf_token"] = secrets.token_hex(32)

    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# --------------------------------------------------
# VULNERABLE ENDPOINT
# --------------------------------------------------

@app.route("/transfer-vuln", methods=["POST"])
def transfer_vulnerable():

    authenticated()

    recipient = request.form.get("recipient", "Unknown")
    amount = int(request.form.get("amount", 0))

    if amount <= 0 or amount > session["balance"]:
        abort(400, "Invalid transfer amount.")

    # No CSRF token validation.
    # No Origin/Referer validation.

    session["balance"] -= amount

    return redirect(
        url_for(
            "home",
            message=f"VULNERABLE: Transferred {amount} points to {recipient}!"
        )
    )


# --------------------------------------------------
# PROTECTED ENDPOINT
# --------------------------------------------------

@app.route("/transfer-protected", methods=["POST"])
def transfer_protected():

    authenticated()

    # 1. Validate the request origin.

    origin = request.headers.get("Origin")

    if origin != VICTIM_ORIGIN:
        abort(403, "Rejected: Invalid request origin.")

    # 2. Validate the CSRF token.

    submitted_token = request.form.get("csrf_token", "")
    stored_token = session.get("csrf_token", "")

    if not stored_token or not hmac.compare_digest(
        submitted_token, stored_token
    ):
        abort(403, "Rejected: Invalid CSRF token.")

    recipient = request.form.get("recipient", "Unknown")
    amount = int(request.form.get("amount", 0))

    if amount <= 0 or amount > session["balance"]:
        abort(400, "Invalid transfer amount.")

    session["balance"] -= amount

    return redirect(
        url_for(
            "home",
            message=f"PROTECTED: Transferred {amount} points to {recipient}!"
        )
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
