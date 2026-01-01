"""File I/O utilities for saving and loading card data."""

import json
import csv
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from ..msr605x.parser import TrackData
from ..msr605x.constants import DataFormat


@dataclass
class CardRecord:
    """A saved card record."""
    timestamp: str
    name: str
    track1: str
    track2: str
    track3: str
    format: str
    coercivity: str
    notes: str = ""


class FileManager:
    """Manages saving and loading of card data."""

    SUPPORTED_FORMATS = [".json", ".csv", ".msr"]

    def __init__(self):
        self._last_directory: Optional[Path] = None

    @property
    def last_directory(self) -> Path:
        """Get last used directory."""
        if self._last_directory and self._last_directory.exists():
            return self._last_directory
        return Path.home()

    def save_tracks_json(self, filepath: Path, tracks: list[TrackData], name: str = "", notes: str = "") -> tuple[bool, str]:
        """
        Save track data to JSON file.

        Args:
            filepath: Path to save file
            tracks: List of TrackData objects
            name: Optional card name
            notes: Optional notes

        Returns:
            Tuple of (success, message)
        """
        try:
            data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "name": name,
                "notes": notes,
                "tracks": []
            }

            for track in tracks:
                data["tracks"].append({
                    "track_number": track.track_number,
                    "data": track.data,
                    "raw_hex": track.raw_data.hex() if track.raw_data else "",
                    "is_valid": track.is_valid,
                    "format": track.format.value if isinstance(track.format, DataFormat) else str(track.format)
                })

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            self._last_directory = filepath.parent
            return True, f"Saved to {filepath.name}"

        except Exception as e:
            return False, f"Save failed: {str(e)}"

    def load_tracks_json(self, filepath: Path) -> tuple[bool, str, list[TrackData]]:
        """
        Load track data from JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            Tuple of (success, message, tracks)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            tracks = []
            for track_data in data.get("tracks", []):
                raw_hex = track_data.get("raw_hex", "")
                raw_bytes = bytes.fromhex(raw_hex) if raw_hex else b""

                format_str = track_data.get("format", "iso")
                try:
                    format_enum = DataFormat(format_str)
                except ValueError:
                    format_enum = DataFormat.ISO

                tracks.append(TrackData(
                    track_number=track_data["track_number"],
                    data=track_data["data"],
                    raw_data=raw_bytes,
                    is_valid=track_data.get("is_valid", True),
                    format=format_enum
                ))

            self._last_directory = filepath.parent
            return True, f"Loaded from {filepath.name}", tracks

        except Exception as e:
            return False, f"Load failed: {str(e)}", []

    def save_tracks_csv(self, filepath: Path, tracks: list[TrackData], name: str = "") -> tuple[bool, str]:
        """
        Save track data to CSV file.

        Args:
            filepath: Path to save file
            tracks: List of TrackData objects
            name: Optional card name

        Returns:
            Tuple of (success, message)
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Name", "Track", "Data", "Valid", "Format"])

                timestamp = datetime.now().isoformat()
                for track in tracks:
                    writer.writerow([
                        timestamp,
                        name,
                        track.track_number,
                        track.data,
                        track.is_valid,
                        track.format.value if isinstance(track.format, DataFormat) else str(track.format)
                    ])

            self._last_directory = filepath.parent
            return True, f"Saved to {filepath.name}"

        except Exception as e:
            return False, f"Save failed: {str(e)}"

    def load_tracks_csv(self, filepath: Path) -> tuple[bool, str, list[TrackData]]:
        """
        Load track data from CSV file.

        Args:
            filepath: Path to CSV file

        Returns:
            Tuple of (success, message, tracks)
        """
        try:
            tracks = []

            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    format_str = row.get("Format", "iso")
                    try:
                        format_enum = DataFormat(format_str)
                    except ValueError:
                        format_enum = DataFormat.ISO

                    tracks.append(TrackData(
                        track_number=int(row["Track"]),
                        data=row["Data"],
                        raw_data=b"",
                        is_valid=row.get("Valid", "True").lower() == "true",
                        format=format_enum
                    ))

            self._last_directory = filepath.parent
            return True, f"Loaded from {filepath.name}", tracks

        except Exception as e:
            return False, f"Load failed: {str(e)}", []

    def save_tracks(self, filepath: Path, tracks: list[TrackData], name: str = "", notes: str = "") -> tuple[bool, str]:
        """
        Save tracks to file, detecting format from extension.

        Args:
            filepath: Path to save file
            tracks: List of TrackData objects
            name: Optional card name
            notes: Optional notes

        Returns:
            Tuple of (success, message)
        """
        suffix = filepath.suffix.lower()

        if suffix == ".csv":
            return self.save_tracks_csv(filepath, tracks, name)
        else:
            # Default to JSON
            return self.save_tracks_json(filepath, tracks, name, notes)

    def load_tracks(self, filepath: Path) -> tuple[bool, str, list[TrackData]]:
        """
        Load tracks from file, detecting format from extension.

        Args:
            filepath: Path to load file

        Returns:
            Tuple of (success, message, tracks)
        """
        suffix = filepath.suffix.lower()

        if suffix == ".csv":
            return self.load_tracks_csv(filepath)
        else:
            # Default to JSON
            return self.load_tracks_json(filepath)

    def export_batch(self, filepath: Path, records: list[CardRecord]) -> tuple[bool, str]:
        """
        Export multiple card records.

        Args:
            filepath: Path to save file
            records: List of CardRecord objects

        Returns:
            Tuple of (success, message)
        """
        try:
            data = {
                "version": "1.0",
                "export_timestamp": datetime.now().isoformat(),
                "count": len(records),
                "records": [asdict(r) for r in records]
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True, f"Exported {len(records)} records"

        except Exception as e:
            return False, f"Export failed: {str(e)}"
