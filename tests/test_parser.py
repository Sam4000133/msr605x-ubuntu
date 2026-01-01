"""Tests for track data parser."""

import pytest
from src.msr605x.parser import TrackParser, TrackData
from src.msr605x.constants import DataFormat


class TestTrackParser:
    """Tests for TrackParser class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.parser = TrackParser()

    def test_build_iso_write_data_all_tracks(self):
        """Test building ISO write data with all tracks."""
        data = self.parser.build_iso_write_data(
            track1="%B4111111111111111^DOE/JOHN^2512101123400001?",
            track2=";4111111111111111=251210110000123?",
            track3=";0123456789?"
        )

        assert data.startswith(b'\x1bs')  # Start marker
        assert b'\x1b\x01' in data  # Track 1 marker
        assert b'\x1b\x02' in data  # Track 2 marker
        assert b'\x1b\x03' in data  # Track 3 marker
        assert data.endswith(b'?\x1c')  # End marker

    def test_build_iso_write_data_single_track(self):
        """Test building ISO write data with single track."""
        data = self.parser.build_iso_write_data(
            track1=None,
            track2=";4111111111111111=2512?",
            track3=None
        )

        assert b'\x1b\x02' in data
        assert b'4111111111111111' in data

    def test_build_raw_write_data(self):
        """Test building raw write data."""
        data = self.parser.build_raw_write_data(
            track1=bytes.fromhex("1A2B3C"),
            track2=None,
            track3=bytes.fromhex("4D5E6F")
        )

        assert b'\x1b\x01' in data
        assert b'\x1a\x2b\x3c' in data
        assert b'\x1b\x03' in data
        assert b'\x4d\x5e\x6f' in data

    def test_clean_track_data(self):
        """Test cleaning track data."""
        dirty_data = "TEST\x00\x00DATA\x1b"
        cleaned = self.parser._clean_track_data(dirty_data, 1)

        assert '\x00' not in cleaned
        assert '\x1b' not in cleaned
        assert 'TEST' in cleaned
        assert 'DATA' in cleaned

    def test_validate_track1_data(self):
        """Test validation of track 1 data."""
        valid_data = "%B4111111111111111^DOE/JOHN^2512?"
        assert self.parser._validate_track_data(valid_data, 1) is True

    def test_validate_empty_data(self):
        """Test validation of empty data."""
        assert self.parser._validate_track_data("", 1) is False
        assert self.parser._validate_track_data("", 2) is False

    def test_format_track_display(self):
        """Test formatting tracks for display."""
        tracks = [
            TrackData(
                track_number=1,
                data="%B1234^TEST^2512?",
                raw_data=b"",
                is_valid=True,
                format=DataFormat.ISO
            ),
            TrackData(
                track_number=2,
                data=";1234=2512?",
                raw_data=b"",
                is_valid=True,
                format=DataFormat.ISO
            ),
        ]

        formatted = self.parser.format_track_display(tracks)

        assert "Track 1" in formatted
        assert "Track 2" in formatted
        assert "[OK]" in formatted
        assert "%B1234^TEST^2512?" in formatted


class TestTrackData:
    """Tests for TrackData dataclass."""

    def test_create_track_data(self):
        """Test creating TrackData instance."""
        track = TrackData(
            track_number=1,
            data="TEST",
            raw_data=b"TEST",
            is_valid=True,
            format=DataFormat.ISO
        )

        assert track.track_number == 1
        assert track.data == "TEST"
        assert track.is_valid is True

    def test_track_data_with_error(self):
        """Test TrackData with error message."""
        track = TrackData(
            track_number=2,
            data="",
            raw_data=b"",
            is_valid=False,
            format=DataFormat.ISO,
            error_message="Read error"
        )

        assert track.is_valid is False
        assert track.error_message == "Read error"
