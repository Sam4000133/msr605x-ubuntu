"""Track data parser for MSR605X responses."""

from dataclasses import dataclass
from typing import Optional
import re

from .constants import (
    TrackSpec, DataFormat, ESC, FS, GS,
    TRACK_START_MARKERS, TRACK_END_MARKER
)


@dataclass
class TrackData:
    """Parsed track data."""
    track_number: int
    data: str
    raw_data: bytes
    is_valid: bool
    format: DataFormat = DataFormat.ISO
    error_message: Optional[str] = None


class TrackParser:
    """
    Parser for MSR605X track data responses.

    Handles ISO, AAMVA, California DMV, and raw data formats.
    """

    # Character sets for validation
    TRACK1_CHARSET = set(' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_')
    TRACK2_CHARSET = set('0123456789:;<=>?')
    TRACK3_CHARSET = set('0123456789:;<=>?')

    def __init__(self):
        self._data_format = DataFormat.ISO

    def set_format(self, format: DataFormat) -> None:
        """Set the expected data format."""
        self._data_format = format

    def parse_iso_response(self, response: bytes) -> list[TrackData]:
        """
        Parse ISO format response from device.

        Args:
            response: Raw bytes from device

        Returns:
            List of TrackData objects for each track.
        """
        tracks = []

        # Response format: ESC s ESC 01 <track1> FS ESC 02 <track2> FS ESC 03 <track3> FS ? ESC status
        # Find track markers
        for track_num in [1, 2, 3]:
            track_data = self._extract_track(response, track_num)
            if track_data:
                tracks.append(track_data)

        return tracks

    def parse_raw_response(self, response: bytes) -> list[TrackData]:
        """
        Parse raw format response from device.

        Args:
            response: Raw bytes from device

        Returns:
            List of TrackData objects with raw binary data.
        """
        tracks = []

        for track_num in [1, 2, 3]:
            track_data = self._extract_track(response, track_num, raw=True)
            if track_data:
                tracks.append(track_data)

        return tracks

    def _extract_track(self, response: bytes, track_num: int, raw: bool = False) -> Optional[TrackData]:
        """
        Extract data for a specific track from response.

        Args:
            response: Full response bytes
            track_num: Track number (1, 2, or 3)
            raw: Whether to treat as raw data

        Returns:
            TrackData object or None if track not found.
        """
        # Track marker is ESC + track_num
        start_marker = bytes([0x1b, track_num])
        end_marker = b'\x1c'  # FS

        try:
            start_idx = response.find(start_marker)
            if start_idx == -1:
                return None

            # Find end of track data
            data_start = start_idx + len(start_marker)
            end_idx = response.find(end_marker, data_start)

            if end_idx == -1:
                # Try to find next track marker or status
                next_track = response.find(bytes([0x1b, track_num + 1]), data_start)
                status_marker = response.find(b'\x1b0', data_start)

                if next_track != -1:
                    end_idx = next_track
                elif status_marker != -1:
                    end_idx = status_marker
                else:
                    end_idx = len(response)

            raw_data = response[data_start:end_idx]

            if raw:
                return TrackData(
                    track_number=track_num,
                    data=raw_data.hex(),
                    raw_data=raw_data,
                    is_valid=len(raw_data) > 0,
                    format=DataFormat.RAW
                )
            else:
                # Decode as ASCII
                try:
                    decoded = raw_data.decode('ascii', errors='replace')
                    # Clean up any control characters except valid sentinels
                    decoded = self._clean_track_data(decoded, track_num)

                    is_valid = self._validate_track_data(decoded, track_num)

                    return TrackData(
                        track_number=track_num,
                        data=decoded,
                        raw_data=raw_data,
                        is_valid=is_valid,
                        format=self._data_format,
                        error_message=None if is_valid else "Invalid characters in track data"
                    )
                except Exception as e:
                    return TrackData(
                        track_number=track_num,
                        data="",
                        raw_data=raw_data,
                        is_valid=False,
                        format=self._data_format,
                        error_message=str(e)
                    )

        except Exception:
            return None

    def _clean_track_data(self, data: str, track_num: int) -> str:
        """
        Clean track data by removing invalid control characters.

        Args:
            data: Decoded string data
            track_num: Track number for format-specific cleaning

        Returns:
            Cleaned string.
        """
        # Remove null bytes and other control characters
        cleaned = ''.join(c for c in data if ord(c) >= 32 or c in '\t')

        # Remove any remaining escape sequences
        cleaned = cleaned.replace('\x1b', '')

        return cleaned.strip()

    def _validate_track_data(self, data: str, track_num: int) -> bool:
        """
        Validate track data against specification.

        Args:
            data: Cleaned track data string
            track_num: Track number

        Returns:
            True if valid, False otherwise.
        """
        if not data:
            return False

        specs = {
            1: (TrackSpec.TRACK_1, self.TRACK1_CHARSET),
            2: (TrackSpec.TRACK_2, self.TRACK2_CHARSET),
            3: (TrackSpec.TRACK_3, self.TRACK3_CHARSET),
        }

        spec, charset = specs.get(track_num, (None, None))
        if not spec:
            return False

        # Check length
        if len(data) > spec['max_chars']:
            return False

        # For ISO format, validate characters
        if self._data_format == DataFormat.ISO:
            # Track 1 is uppercase alphanumeric
            if track_num == 1:
                # Allow all printable ASCII for flexibility
                return all(32 <= ord(c) <= 95 for c in data)
            else:
                # Tracks 2 and 3 are numeric with some special chars
                return all(c in charset or c in '%?;' for c in data)

        return True

    def build_iso_write_data(
        self,
        track1: Optional[str] = None,
        track2: Optional[str] = None,
        track3: Optional[str] = None
    ) -> bytes:
        """
        Build ISO format write data payload.

        Args:
            track1: Track 1 data (alphanumeric)
            track2: Track 2 data (numeric)
            track3: Track 3 data (numeric)

        Returns:
            Bytes to send to device.
        """
        data = b'\x1bs'  # Start of data

        # Track 1
        data += b'\x1b\x01'
        if track1:
            data += track1.upper().encode('ascii')
        data += b'\x1c'

        # Track 2
        data += b'\x1b\x02'
        if track2:
            data += track2.encode('ascii')
        data += b'\x1c'

        # Track 3
        data += b'\x1b\x03'
        if track3:
            data += track3.encode('ascii')
        data += b'\x1c'

        data += b'?\x1c'  # End sentinel and separator

        return data

    def build_raw_write_data(
        self,
        track1: Optional[bytes] = None,
        track2: Optional[bytes] = None,
        track3: Optional[bytes] = None
    ) -> bytes:
        """
        Build raw format write data payload.

        Args:
            track1: Track 1 raw bytes
            track2: Track 2 raw bytes
            track3: Track 3 raw bytes

        Returns:
            Bytes to send to device.
        """
        data = b'\x1bs'  # Start of data

        # Track 1
        data += b'\x1b\x01'
        if track1:
            data += track1
        data += b'\x1c'

        # Track 2
        data += b'\x1b\x02'
        if track2:
            data += track2
        data += b'\x1c'

        # Track 3
        data += b'\x1b\x03'
        if track3:
            data += track3
        data += b'\x1c'

        data += b'?\x1c'

        return data

    def parse_aamva(self, track_data: str) -> dict:
        """
        Parse AAMVA format driver's license data.

        Args:
            track_data: Combined track data string

        Returns:
            Dictionary with parsed fields.
        """
        result = {}

        # AAMVA format varies by jurisdiction
        # Basic parsing for common fields
        patterns = {
            'iin': r'^%([A-Z]{2})',  # Issuer Identification Number (state)
            'license_number': r'([A-Z0-9]+)\^',
            'last_name': r'\^([A-Z]+)\$',
            'first_name': r'\$([A-Z]+)\$',
            'middle_name': r'\$\$([A-Z]*)\^',
        }

        for field, pattern in patterns.items():
            match = re.search(pattern, track_data)
            if match:
                result[field] = match.group(1)

        return result

    def format_track_display(self, tracks: list[TrackData]) -> str:
        """
        Format track data for display.

        Args:
            tracks: List of TrackData objects

        Returns:
            Formatted string for display.
        """
        lines = []
        for track in tracks:
            status = "OK" if track.is_valid else "ERROR"
            lines.append(f"Track {track.track_number} [{status}]: {track.data}")
            if track.error_message:
                lines.append(f"  Error: {track.error_message}")
        return '\n'.join(lines)
