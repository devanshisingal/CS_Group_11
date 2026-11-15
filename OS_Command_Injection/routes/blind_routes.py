from flask import Blueprint, render_template, request
import subprocess
import socket
import re

blind_bp = Blueprint('blind', __name__)

@blind_bp.route('/blind', methods=['POST'])
def blind_vulnerable():
    domain = request.form.get('domain')
    # VULNERABLE: Output redirected to /dev/null, but shell executes command chain (e.g., sleep 5)
    command = f"nslookup {domain} > /dev/null 2>&1"
    subprocess.run(command, shell=True)
    return render_template('index.html', blind_output="Lookup request processed (Blind: check response delay or logs).")

@blind_bp.route('/blind-secure', methods=['POST'])
def blind_secure():
    domain = request.form.get('domain')
    # MITIGATION: Avoid OS shell entirely; use native library safe lookup
    if not re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", domain):
        return render_template('index.html', blind_output="[BLOCKED] Invalid domain format.")
    try:
        ip = socket.gethostbyname(domain)
        output = f"Secure Native Lookup Successful. Resolved IP: {ip}"
    except socket.gaierror:
        output = "Lookup failed: Host not found."
    return render_template('index.html', blind_output=output)
