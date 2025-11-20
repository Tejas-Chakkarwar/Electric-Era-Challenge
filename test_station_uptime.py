#Unit Tests
import pytest
import tempfile
import os
from station_uptime import (
    parse_input_file,
    merge_intervals,
    calculate_total_time,
    calculate_station_uptime
)


class TestMergeIntervals:
    """Tests for the interval merging algorithm."""

    def test_empty_intervals(self):
        """Test with no intervals."""
        assert merge_intervals([]) == []

    def test_single_interval(self):
        """Test with one interval."""
        assert merge_intervals([(0, 100)]) == [(0, 100)]

    def test_non_overlapping_intervals(self):
        """Test intervals that don't overlap."""
        intervals = [(0, 10), (20, 30), (40, 50)]
        assert merge_intervals(intervals) == [(0, 10), (20, 30), (40, 50)]

    def test_overlapping_intervals(self):
        """Test overlapping intervals merge correctly."""
        intervals = [(0, 30), (20, 50)]
        assert merge_intervals(intervals) == [(0, 50)]

    def test_adjacent_intervals(self):
        """Test adjacent intervals merge (end == start)."""
        intervals = [(0, 50), (50, 100)]
        assert merge_intervals(intervals) == [(0, 100)]

    def test_contained_intervals(self):
        """Test when one interval contains another."""
        intervals = [(0, 100), (25, 75)]
        assert merge_intervals(intervals) == [(0, 100)]

    def test_multiple_overlapping(self):
        """Test multiple overlapping intervals."""
        intervals = [(0, 30), (20, 50), (40, 80), (100, 120)]
        assert merge_intervals(intervals) == [(0, 80), (100, 120)]

    def test_unsorted_intervals(self):
        """Test that unsorted intervals are handled correctly."""
        intervals = [(50, 100), (0, 30), (20, 60)]
        assert merge_intervals(intervals) == [(0, 100)]

    def test_same_start_different_end(self):
        """Test intervals with same start but different ends."""
        intervals = [(0, 50), (0, 100)]
        assert merge_intervals(intervals) == [(0, 100)]


class TestCalculateTotalTime:
    """Tests for total time calculation."""

    def test_empty_intervals(self):
        """Test with no intervals."""
        assert calculate_total_time([]) == 0

    def test_single_interval(self):
        """Test with one interval."""
        assert calculate_total_time([(0, 100)]) == 100

    def test_multiple_intervals(self):
        """Test with multiple intervals."""
        intervals = [(0, 50), (100, 200)]
        assert calculate_total_time(intervals) == 150

    def test_large_values(self):
        """Test with large time values (uint64 range)."""
        intervals = [(0, 10000000000), (20000000000, 30000000000)]
        assert calculate_total_time(intervals) == 20000000000


class TestParseInputFile:
    """Tests for input file parsing."""

    def test_valid_input(self):
        """Test parsing a valid input file."""
        content = """[Stations]
0 1001 1002
1 1003

[Charger Availability Reports]
1001 0 100 true
1002 50 150 false
1003 0 200 true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            f.flush()

            try:
                stations, reports = parse_input_file(f.name)

                assert stations == {0: [1001, 1002], 1: [1003]}
                assert len(reports) == 3
                assert (1001, 0, 100, True) in reports
                assert (1002, 50, 150, False) in reports
                assert (1003, 0, 200, True) in reports
            finally:
                os.unlink(f.name)

    def test_missing_file(self):
        """Test error handling for missing file."""
        with pytest.raises(ValueError, match="not found"):
            parse_input_file("nonexistent_file.txt")

    def test_missing_stations_section(self):
        """Test error when stations section is missing."""
        content = """[Charger Availability Reports]
1001 0 100 true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            f.flush()

            try:
                with pytest.raises(ValueError):
                    parse_input_file(f.name)
            finally:
                os.unlink(f.name)

    def test_invalid_boolean(self):
        """Test error handling for invalid boolean value."""
        content = """[Stations]
0 1001

[Charger Availability Reports]
1001 0 100 maybe
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            f.flush()

            try:
                with pytest.raises(ValueError, match="Invalid up value"):
                    parse_input_file(f.name)
            finally:
                os.unlink(f.name)

    def test_unknown_charger_id(self):
        """Test error handling for unknown charger ID in reports."""
        content = """[Stations]
0 1001

[Charger Availability Reports]
9999 0 100 true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            f.flush()

            try:
                with pytest.raises(ValueError, match="Unknown charger ID"):
                    parse_input_file(f.name)
            finally:
                os.unlink(f.name)

    def test_duplicate_station_id(self):
        """Test error handling for duplicate station IDs."""
        content = """[Stations]
0 1001
0 1002

[Charger Availability Reports]
1001 0 100 true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            f.flush()

            try:
                with pytest.raises(ValueError, match="Duplicate station ID"):
                    parse_input_file(f.name)
            finally:
                os.unlink(f.name)

    def test_duplicate_charger_id(self):
        """Test error handling for duplicate charger IDs."""
        content = """[Stations]
0 1001
1 1001

[Charger Availability Reports]
1001 0 100 true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            f.flush()

            try:
                with pytest.raises(ValueError, match="Duplicate charger ID"):
                    parse_input_file(f.name)
            finally:
                os.unlink(f.name)

    def test_invalid_time_range(self):
        """Test error handling for start >= end."""
        content = """[Stations]
0 1001

[Charger Availability Reports]
1001 100 50 true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            f.flush()

            try:
                with pytest.raises(ValueError, match="Invalid time range"):
                    parse_input_file(f.name)
            finally:
                os.unlink(f.name)

    def test_station_with_no_chargers(self):
        """Test station defined with no chargers."""
        content = """[Stations]
0

[Charger Availability Reports]
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            f.flush()

            try:
                stations, reports = parse_input_file(f.name)
                assert stations == {0: []}
                assert reports == []
            finally:
                os.unlink(f.name)


class TestCalculateStationUptime:
    """Tests for station uptime calculation."""

    def test_single_charger_always_up(self):
        """Test station with one charger always up."""
        stations = {0: [1001]}
        reports = [(1001, 0, 100, True)]

        uptimes = calculate_station_uptime(stations, reports)
        assert uptimes[0] == 100

    def test_single_charger_always_down(self):
        """Test station with one charger always down."""
        stations = {0: [1001]}
        reports = [(1001, 0, 100, False)]

        uptimes = calculate_station_uptime(stations, reports)
        assert uptimes[0] == 0

    def test_single_charger_partial_uptime(self):
        """Test station with partial uptime."""
        stations = {0: [1001]}
        reports = [
            (1001, 0, 50, True),
            (1001, 50, 100, False)
        ]

        uptimes = calculate_station_uptime(stations, reports)
        assert uptimes[0] == 50

    def test_multiple_chargers_overlap(self):
        """Test multiple chargers with overlapping up times."""
        stations = {0: [1001, 1002]}
        reports = [
            (1001, 0, 60, True),
            (1002, 40, 100, True)
        ]

        uptimes = calculate_station_uptime(stations, reports)
        # Up from 0-100, total 100
        assert uptimes[0] == 100

    def test_gap_counts_as_downtime(self):
        """Test that gaps between reports count as downtime."""
        stations = {0: [1001]}
        reports = [
            (1001, 0, 50, True),
            (1001, 100, 200, True)
        ]

        uptimes = calculate_station_uptime(stations, reports)
        # Up: 50 + 100 = 150, Total: 200, Uptime: 75%
        assert uptimes[0] == 75

    def test_floor_rounding(self):
        """Test that percentages are floored."""
        stations = {0: [1001]}
        reports = [
            (1001, 0, 10, True),
            (1001, 10, 20, False),
            (1001, 20, 30, True)
        ]

        uptimes = calculate_station_uptime(stations, reports)
        # Up: 20, Total: 30, Uptime: 66.67% -> 66%
        assert uptimes[0] == 66

    def test_multiple_stations(self):
        """Test calculating uptime for multiple stations."""
        stations = {0: [1001], 1: [1002], 2: [1003]}
        reports = [
            (1001, 0, 100, True),
            (1002, 0, 100, False),
            (1003, 0, 50, True),
            (1003, 50, 100, False)
        ]

        uptimes = calculate_station_uptime(stations, reports)
        assert uptimes[0] == 100
        assert uptimes[1] == 0
        assert uptimes[2] == 50

    def test_station_with_no_reports(self):
        """Test station with no charger reports."""
        stations = {0: [1001], 1: [1002]}
        reports = [(1001, 0, 100, True)]  # No reports for 1002

        uptimes = calculate_station_uptime(stations, reports)
        assert uptimes[0] == 100
        assert uptimes[1] == 0

    def test_large_time_values(self):
        """Test with large time values."""
        stations = {0: [1001]}
        reports = [
            (1001, 0, 10000000000, True),
            (1001, 10000000000, 20000000000, False)
        ]

        uptimes = calculate_station_uptime(stations, reports)
        assert uptimes[0] == 50

    def test_input_1_example(self):
        """Test with input_1.txt example data."""
        stations = {0: [1001, 1002], 1: [1003], 2: [1004]}
        reports = [
            (1001, 0, 50000, True),
            (1001, 50000, 100000, True),
            (1002, 50000, 100000, True),
            (1003, 25000, 75000, False),
            (1004, 0, 50000, True),
            (1004, 100000, 200000, True)
        ]

        uptimes = calculate_station_uptime(stations, reports)
        assert uptimes[0] == 100
        assert uptimes[1] == 0
        assert uptimes[2] == 75

    def test_input_2_example(self):
        """Test with input_2.txt example data."""
        stations = {0: [0], 1: [1]}
        reports = [
            (0, 10, 20, True),
            (0, 20, 30, False),
            (0, 30, 40, True),
            (1, 0, 1, True)
        ]

        uptimes = calculate_station_uptime(stations, reports)
        assert uptimes[0] == 66
        assert uptimes[1] == 100


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_single_nanosecond_period(self):
        """Test with minimum time period (1 ns)."""
        stations = {0: [1001]}
        reports = [(1001, 0, 1, True)]

        uptimes = calculate_station_uptime(stations, reports)
        assert uptimes[0] == 100

    def test_charger_id_zero(self):
        """Test with charger ID of 0."""
        stations = {0: [0]}
        reports = [(0, 0, 100, True)]

        uptimes = calculate_station_uptime(stations, reports)
        assert uptimes[0] == 100

    def test_station_id_zero(self):
        """Test with station ID of 0."""
        stations = {0: [1001]}
        reports = [(1001, 0, 100, True)]

        uptimes = calculate_station_uptime(stations, reports)
        assert uptimes[0] == 100

    def test_many_small_intervals(self):
        """Test with many small intervals."""
        stations = {0: [1001]}
        # 10 intervals, alternating up/down
        reports = [(1001, i * 10, (i + 1) * 10, i % 2 == 0) for i in range(10)]

        uptimes = calculate_station_uptime(stations, reports)
        # 5 up intervals out of 10, so 50%
        assert uptimes[0] == 50

    def test_exactly_one_percent(self):
        """Test uptime of exactly 1%."""
        stations = {0: [1001]}
        reports = [
            (1001, 0, 1, True),
            (1001, 1, 100, False)
        ]

        uptimes = calculate_station_uptime(stations, reports)
        assert uptimes[0] == 1

    def test_just_under_one_percent(self):
        """Test uptime just under 1% (should floor to 0)."""
        stations = {0: [1001]}
        reports = [
            (1001, 0, 1, True),
            (1001, 1, 200, False)
        ]

        uptimes = calculate_station_uptime(stations, reports)
        # 1/200 = 0.5% -> floors to 0%
        assert uptimes[0] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])