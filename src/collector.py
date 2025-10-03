# # src/collector.py
# from flask import Flask, request, jsonify
# import logging

# app = Flask(__name__)
# logging.basicConfig(level=logging.INFO)

# @app.route("/metrics", methods=["POST"])
# def metrics():
#     data = request.get_json(force=True)
#     app.logger.info("Received metrics: %s", data)
#     return jsonify({"status": "ok"}), 200

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=False)


# src/collector.py
from flask import Flask, request, jsonify
import logging, smtplib, ssl, os
from email.mime.text import MIMEText

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Email settings (use Gmail for demo)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "04monika11@gmail.com")
PASSWORD = os.getenv("EMAIL_PASSWORD", "olab wmkr ricc vdxb")   # generate from Gmail
ALERT_TO = os.getenv("ALERT_TO", "monikam102004@gmail.com")

def send_email_alert(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = ALERT_TO
    try:
        app.logger.info(f"DEBUG: SMTP_SERVER={SMTP_SERVER}, SMTP_PORT={SMTP_PORT}")
        app.logger.info(f"DEBUG: SENDER_EMAIL={SENDER_EMAIL}, ALERT_TO={ALERT_TO}")
        app.logger.info(f"DEBUG: PASSWORD length={len(PASSWORD) if PASSWORD else 'None'}")
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            app.logger.info("DEBUG: Attempting SMTP login")
            server.login(SENDER_EMAIL, PASSWORD)
            app.logger.info("DEBUG: SMTP login successful")
            server.sendmail(SENDER_EMAIL, ALERT_TO, msg.as_string())
        app.logger.info("✅ Alert email sent: %s", subject)
    except Exception as e:
        app.logger.error("❌ Failed to send email: %s", e)

@app.route("/metrics", methods=["POST"])
def metrics():
    import subprocess
    import platform
    import re

    data = request.get_json(force=True)
    app.logger.info("Received metrics: %s", data)

    # 🔴 Anomaly detection
    alerts = []

    # High CPU usage
    if data.get("cpu", 0) > 85:
        alerts.append(f"⚠ High CPU Alert!\nHost: {data['host']}\nCPU: {data['cpu']}%\nMemory: {data['mem']}%")

    # High Disk usage
    if data.get("disk", 0) > 90:
        alerts.append(f"⚠ High Disk Usage Alert!\nHost: {data['host']}\nDisk Usage: {data['disk']}%")

    # Network connectivity check (ping google.com)
    def ping(host="8.8.8.8"):
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", host]
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
            # Extract time from ping output
            match = re.search(r"time[=<]\s*(\d+\.?\d*)\s*ms", output)
            if match:
                latency = float(match.group(1))
                return True, latency
            return True, None
        except Exception as e:
            app.logger.error(f"Ping failed: {e}")
            return False, None

    reachable, latency = ping()
    if not reachable:
        alerts.append(f"⚠ Network Connectivity Alert!\nHost: {data['host']}\nCannot reach 8.8.8.8")
    elif latency and latency > 100:
        alerts.append(f"⚠ High Network Latency Alert!\nHost: {data['host']}\nLatency: {latency} ms")

    # Send alerts if any
    for alert_msg in alerts:
        send_email_alert("⚠ Server Alert", alert_msg)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

