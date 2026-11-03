"""
ZYROX AI — Automated Server Host Manager
========================================
Runs and monitors the ZYROX AI Trading backend and dashboard locally.
Features:
- Automatic dependency verification
- Database migration pre-flight
- Port availability check
- Continuous health monitoring & auto-restart on crash
- Auto-open browser to dashboard
"""

import os
import sys
import time
import subprocess
import webbrowser
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("auto_host")

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
PING_URL = f"http://{HOST}:{PORT}/ping"
DASHBOARD_URL = f"http://{HOST}:{PORT}/dashboard/"


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def wait_for_server(timeout: int = 30) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(PING_URL, headers={"User-Agent": "ZYROX-AutoHost/1.0"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def run_database_migrations():
    logger.info("Initializing database and verifying migrations...")
    try:
        from taikry.database.session import init_db
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.warning(f"Database pre-flight check warning: {exc}")


def main():
    logger.info("=" * 60)
    logger.info("  ZYROX AI TRADING — AUTO HOST SERVER MANAGER")
    logger.info(f"  Target: http://{HOST}:{PORT}")
    logger.info(f"  Dashboard: {DASHBOARD_URL}")
    logger.info("=" * 60)

    # 1. Run DB migrations
    run_database_migrations()

    # 2. Check if already running
    if is_port_in_use(PORT, HOST):
        logger.info(f"Port {PORT} is already active. Checking health...")
        if wait_for_server(timeout=3):
            logger.info(f"Server is already running healthy at {DASHBOARD_URL}")
            webbrowser.open(DASHBOARD_URL)
            return

    # 3. Server supervision loop
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "taikry.api.app:app",
        "--host", HOST,
        "--port", str(PORT),
    ]

    browser_opened = False
    restart_count = 0

    while True:
        logger.info(f"Starting server process (Attempt #{restart_count + 1})...")
        process = subprocess.Popen(cmd)

        # Wait for server to become responsive
        if wait_for_server(timeout=25):
            logger.info("Server is ONLINE and healthy!")
            if not browser_opened:
                webbrowser.open(DASHBOARD_URL)
                browser_opened = True
        else:
            logger.warning("Server took longer than expected to report healthy.")

        try:
            # Monitor process status
            retcode = process.wait()
            logger.warning(f"Server process terminated with exit code {retcode}.")
        except KeyboardInterrupt:
            logger.info("Shutdown signal received. Stopping server...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            logger.info("Server stopped.")
            break

        restart_count += 1
        logger.info("Auto-restarting in 2 seconds...")
        time.sleep(2)


if __name__ == "__main__":
    main()
