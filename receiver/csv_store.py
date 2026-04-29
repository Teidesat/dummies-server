"""Simple CSV persistence for receiver incoming message data."""

from __future__ import annotations

import csv
import os
from datetime import datetime, timezone


class ReceiverCSVStore:
    """Persists received messages and retrieves the latest message."""

    FIELDNAMES = ["timestamp", "experiment_id", "message", "source"]

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        directory = os.path.dirname(self.file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            with open(self.file_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.FIELDNAMES)
                writer.writeheader()

    def append_message(self, experiment_id: str, message: str, source: str):
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "experiment_id": experiment_id,
            "message": message,
            "source": source,
        }
        with open(self.file_path, "a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.FIELDNAMES)
            writer.writerow(row)

    def get_latest_message(self) -> str:
        latest = None
        with open(self.file_path, "r", newline="", encoding="utf-8") as csv_file:
            for row in csv.DictReader(csv_file):
                latest = row
        if latest is None:
            return ""
        return latest["message"]


def default_receiver_csv_path() -> str:
    return os.getenv(
        "RECEIVER_DATA_CSV",
        os.path.join(os.path.dirname(__file__), "data", "receiver_data.csv"),
    )
