"""Simple CSV persistence for transmitter message and settings data."""

from __future__ import annotations

import csv
import os
from datetime import datetime, timezone


class TransmitterCSVStore:
    """Persists transmitter experiments in a CSV file and retrieves the latest row."""

    FIELDNAMES = [
        "timestamp",
        "experiment_id",
        "message",
        "dummy_distance",
        "transmitter_angle",
        "led_intensity",
        "blinking_frequency",
        "messages_batch",
    ]

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

    def append_experiment(self, data: dict):
        settings = data.get("settings", {})
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "experiment_id": data.get("experiment_id", ""),
            "message": data.get("message", ""),
            "dummy_distance": settings.get("dummy_distance", ""),
            "transmitter_angle": settings.get("transmitter_angle", ""),
            "led_intensity": settings.get("led_intensity", ""),
            "blinking_frequency": settings.get("blinking_frequency", ""),
            "messages_batch": settings.get("messages_batch", ""),
        }
        with open(self.file_path, "a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.FIELDNAMES)
            writer.writerow(row)

    def get_latest_experiment(self) -> dict | None:
        latest = None
        with open(self.file_path, "r", newline="", encoding="utf-8") as csv_file:
            for row in csv.DictReader(csv_file):
                latest = row
        return latest


def default_transmitter_csv_path() -> str:
    return os.getenv(
        "TRANSMITTER_DATA_CSV",
        os.path.join(os.path.dirname(__file__), "data", "transmitter_data.csv"),
    )
