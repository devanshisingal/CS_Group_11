from flask import Blueprint, render_template, request
import subprocess
import re

inband_bp = Blueprint('inband', __name__)

@inband_bp.route('/inband', methods=['POST'])
def inband_vulnerable():
    target = request.form.get('target')
    # VULNERABLE: Direct string concatenation with shell=True
    command = f"ping -c 1 {target}"
    try:
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output
    return render_template('index.html', inband_output=output)

@inband_bp.route('/inband-secure', methods=['POST'])
def inband_secure():
    target = request.form.get('target')
    # MITIGATION: Allow-list regex + shell=False (argument vector)
    if not re.match(r"^[a-zA-Z0-9.-]+$", target):
        return render_template('index.html', inband_output="[BLOCKED] Invalid characters detected by input validation.")
    try:
        output = subprocess.check_output(['ping', '-c', '1', target], text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output
    return render_template('index.html', inband_output=output)
