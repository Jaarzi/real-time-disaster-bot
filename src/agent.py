# src/agent.py (improved)
import os
import time
import json
import socket
import signal
import logging
import psutil
import requests

# Config from environment (safe defaults)
COLLECTOR = os.getenv("COLLECTOR_URL", "http://localhost:5000/metrics")
INTERVAL = float(os.getenv("INTERVAL", "5"))          # seconds between sends
HOST = os.getenv("HOST", socket.gethostname())
DISK_PATH = os.getenv("DISK_PATH", os.path.abspath(os.sep))  # root by default
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "5"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

stop_signal = False

def _handle_signal(signum, frame):
    global stop_signal
    logging.info("Received stop signal (%s). Graceful shutdown requested.", signum)
    stop_signal = True

# Bind ctrl-c and termination
signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)

def collect():
    """Collect CPU, memory, disk, timestamp and host."""
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "mem": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage(DISK_PATH).percent,
        "timestamp": time.time(),
        "host": HOST
    }

def send(payload):
    """Send payload with simple retry/backoff."""
    headers = {"Content-Type": "application/json"}
    attempt = 0
    backoff = 1
    while attempt < MAX_RETRIES and not stop_signal:
        try:
            resp = requests.post(COLLECTOR, json=payload, timeout=HTTP_TIMEOUT, headers=headers)
            resp.raise_for_status()
            logging.info("Sent metrics: %s", payload)
            return True
        except Exception as e:
            attempt += 1
            logging.warning("Send failed (attempt %d/%d): %s. Retrying in %ds", attempt, MAX_RETRIES, e, backoff)
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)
    logging.error("Giving up on sending payload: %s", payload)
    return False

if __name__ == "__main__":
    logging.info("Agent starting: collector=%s interval=%s disk_path=%s", COLLECTOR, INTERVAL, DISK_PATH)
    while not stop_signal:
        payload = collect()
        send(payload)
        # sleep as small increments so we can catch signals quickly
        slept = 0.0
        while slept < INTERVAL and not stop_signal:
            time.sleep(0.5)
            slept += 0.5
    logging.info("Agent stopped.")
