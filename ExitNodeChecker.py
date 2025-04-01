import requests
import json
import sqlite3
import logging
from datetime import datetime, timezone

# Constants
TOR_EXIT_NODES_URL = "https://check.torproject.org/torbulkexitlist"
DB_FILE = "firewall_block_list.db"
EXPORT_JSON_FILE = "firewall_block_list_export.json"
LOG_FILE = "firewall_block_list.log"

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def fetch_tor_exit_nodes():
    """Fetch the current list of Tor exit nodes."""
    try:
        response = requests.get(TOR_EXIT_NODES_URL)
        response.raise_for_status()
        return set(response.text.strip().split("\n"))
    except requests.RequestException as e:
        logging.error(f"Failed to fetch Tor exit nodes: {e}")
        raise

def init_db():
    """Initialize the SQLite database and create the table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocked_ips (
            ip TEXT PRIMARY KEY,
            added_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def load_blocked_ips():
    """Load the existing blocked IPs from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT ip FROM blocked_ips")
    blocked_ips = {row[0] for row in cursor.fetchall()}
    conn.close()
    return blocked_ips

def insert_new_threats(new_threats):
    """Insert new threats into the database with a timestamp."""
    if not new_threats:
        return

    timestamp = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT OR IGNORE INTO blocked_ips (ip, added_at) VALUES (?, ?)",
        [(ip, timestamp) for ip in new_threats],
    )
    conn.commit()
    conn.close()
    logging.info(f"Inserted {len(new_threats)} new threats into the database.")

def export_to_json():
    """Export the blocked IPs from the database to a JSON file, including timestamps."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT ip, added_at FROM blocked_ips ORDER BY added_at DESC")
    blocked_ips = [{"ip": row[0], "added_at": row[1]} for row in cursor.fetchall()]
    conn.close()

    with open(EXPORT_JSON_FILE, "w") as file:
        json.dump({"blocked_ips": blocked_ips}, file, indent=4)

    logging.info(f"Exported {len(blocked_ips)} blocked IPs to {EXPORT_JSON_FILE}")

def main():
    try:
        init_db()
        tor_ips = fetch_tor_exit_nodes()
        blocked_ips = load_blocked_ips()
        new_threats = tor_ips - blocked_ips

        if new_threats:
            logging.info(f"New threats detected: {len(new_threats)} IPs")
            insert_new_threats(new_threats)
        else:
            logging.info("No new threats detected. All Tor exit nodes are already blocked.")

        export_to_json()

    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
