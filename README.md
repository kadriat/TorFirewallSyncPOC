# Firewall Block List

This repository contains a Python script that automates the process of:

1. Fetching the current list of Tor Exit Nodes.
2. Comparing the list with an existing firewall block list.
3. Inserting new threats (unblocked Tor Exit Nodes) into an SQLite database.
4. Exporting the updated block list (including timestamps) to a JSON file.

## Features

- **Fetch Tor Exit Nodes**: The script fetches the latest list of Tor Exit Nodes from the Tor Project.
- **Database Management**: It maintains an SQLite database to store blocked IPs and their timestamps.
- **Logging**: Logs the process to `firewall_block_list.log` for tracking changes and errors.
- **Export to JSON**: Exports the final list of blocked IPs (with timestamps) to `firewall_block_list_export.json`.
- **Timestamp Support**: Records timestamps for when IPs were added to the block list.

## Requirements

- Python 3.x
- `requests` library for HTTP requests
- SQLite (comes built-in with Python)

To install the required Python package:

    ```sh
    pip install requests
    ```

## Usage

1. Clone the repository:

    ```sh
    git clone https://github.com/kadriat/TorFirewallSyncPOC.git
    cd TorFirewallSyncPOC
    ```

2. Run the script to fetch the latest Tor Exit Nodes, update the block list, and export the data:

    ```sh
    python3 ExitNodeChecker.py
    ```

3. The script will:

- Fetch the list of Tor Exit Nodes from TorProject.

- Compare it with the current firewall block list stored in an SQLite database.

- Insert any new threats into the database.

- Export the updated list of blocked IPs to firewall_block_list_export.json.

- Log all activities in firewall_block_list.log.

## Files

- ExitNodeChecker.py: Main script for fetching Tor Exit Nodes, updating the block list, and exporting data.

- firewall_block_list.json: The original list of the blocked IPs

- firewall_block_list.db: SQLite database file where blocked IPs and their timestamps are stored.

- firewall_block_list_export.json: JSON file containing the list of blocked IPs with timestamps.

- firewall_block_list.log: Log file to track script activities, including errors and new threats.

## Example of Exported JSON

```json
{
    "blocked_ips": [
        {
            "ip": "192.168.1.10",
            "added_at": "2025-03-31T12:34:56.789123"
        },
        {
            "ip": "203.0.113.45",
            "added_at": "2025-03-30T15:22:33.456789"
        }
    ]
}
```


## Testing

1. run the script once

        python3 ExitNodeChecker.py

2. Connect to the database using sqlite3

        sqlite3 firewall_block_list.db

3. Drop a row from the table

        sqlite> DELETE FROM blocked_ips WHERE ip='5.255.99.147';

4. Run the script again

        python3 ExitNodeChecker.py

5. Check the logs that the row was re-added

        $ cat firewall_block_list.log
        2025-03-31 21:51:13,274 - INFO - New threats detected: 1223 IPs
        2025-03-31 21:51:13,285 - INFO - Inserted 1223 new threats into the database.
        2025-03-31 21:51:13,288 - INFO - Exported 1223 blocked IPs to firewall_block_list_export.json
        2025-03-31 21:57:55,286 - INFO - New threats detected: 1 IPs
        2025-03-31 21:57:55,297 - INFO - Inserted 1 new threats into the database.
        2025-03-31 21:57:55,299 - INFO - Exported 1223 blocked IPs to firewall_block_list_export.json
