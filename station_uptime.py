#Station Uptime Calculator

import sys
from typing import Dict, List, Tuple

#Parse the input file and extract station-charger mappings and availability reports.
def parse_input_file(file_path: str) -> Tuple[Dict[int, List[int]], List[Tuple[int, int, int, bool]]]:

    stations: Dict[int, List[int]] = {}
    reports: List[Tuple[int, int, int, bool]] = []

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise ValueError(f"Input file not found: {file_path}")
    except IOError as e:
        raise ValueError(f"Error reading input file: {e}")

    # Track which section we're in
    current_section = None
    charger_to_station: Dict[int, int] = {}  # For validation

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Check for section headers
        if line == "[Stations]":
            current_section = "stations"
            continue
        elif line == "[Charger Availability Reports]":
            current_section = "reports"
            continue

        if current_section == "stations":
            parts = line.split()
            if len(parts) < 1:
                raise ValueError(f"Invalid station line at line {line_num}")

            try:
                station_id = int(parts[0])
                if station_id < 0 or station_id > 4294967295:  # uint32 range
                    raise ValueError(f"Station ID out of uint32 range at line {line_num}")

                charger_ids = []
                for i in range(1, len(parts)):
                    charger_id = int(parts[i])
                    if charger_id < 0 or charger_id > 4294967295:  # uint32 range
                        raise ValueError(f"Charger ID out of uint32 range at line {line_num}")

                    # Check for duplicate charger IDs across stations
                    if charger_id in charger_to_station:
                        raise ValueError(f"Duplicate charger ID {charger_id} at line {line_num}")

                    charger_to_station[charger_id] = station_id
                    charger_ids.append(charger_id)

                # Check for duplicate station IDs
                if station_id in stations:
                    raise ValueError(f"Duplicate station ID {station_id} at line {line_num}")

                stations[station_id] = charger_ids

            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Invalid integer at line {line_num}")
                raise

        elif current_section == "reports":
            parts = line.split()
            if len(parts) != 4:
                raise ValueError(f"Invalid report format at line {line_num}: expected 4 fields")

            try:
                charger_id = int(parts[0])
                start_time = int(parts[1])
                end_time = int(parts[2])
                up_str = parts[3].lower()

                # Validate ranges
                if charger_id < 0 or charger_id > 4294967295:
                    raise ValueError(f"Charger ID out of uint32 range at line {line_num}")
                if start_time < 0 or start_time > 18446744073709551615:  # uint64 range
                    raise ValueError(f"Start time out of uint64 range at line {line_num}")
                if end_time < 0 or end_time > 18446744073709551615:
                    raise ValueError(f"End time out of uint64 range at line {line_num}")

                # Validate up field
                if up_str == "true":
                    is_up = True
                elif up_str == "false":
                    is_up = False
                else:
                    raise ValueError(f"Invalid up value at line {line_num}: must be 'true' or 'false'")

                # Validate time range
                if start_time >= end_time:
                    raise ValueError(f"Invalid time range at line {line_num}: start >= end")

                # Validate charger exists
                if charger_id not in charger_to_station:
                    raise ValueError(f"Unknown charger ID {charger_id} at line {line_num}")

                reports.append((charger_id, start_time, end_time, is_up))

            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Invalid integer at line {line_num}")
                raise

        elif current_section is None:
            raise ValueError(f"Data found before section header at line {line_num}")

    if not stations:
        raise ValueError("No stations defined in input file")

    return stations, reports

#Merge overlapping intervals.
def merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not intervals:
        return []

    # Sort by start time
    sorted_intervals = sorted(intervals)
    merged = [sorted_intervals[0]]

    for start, end in sorted_intervals[1:]:
        last_start, last_end = merged[-1]

        # If current interval overlaps or is adjacent to the last merged interval
        if start <= last_end:
            # Extend the last interval if necessary
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))

    return merged

#Calculate total time covered by merged intervals
def calculate_total_time(intervals: List[Tuple[int, int]]) -> int:
    return sum(end - start for start, end in intervals)

#Calculate uptime percentage for each station
def calculate_station_uptime(
    stations: Dict[int, List[int]],
    reports: List[Tuple[int, int, int, bool]]
) -> Dict[int, int]:
    # Build charger to station mapping
    charger_to_station: Dict[int, int] = {}
    for station_id, charger_ids in stations.items():
        for charger_id in charger_ids:
            charger_to_station[charger_id] = station_id

    # Group reports by station
    station_reports: Dict[int, List[Tuple[int, int, bool]]] = {sid: [] for sid in stations}

    for charger_id, start_time, end_time, is_up in reports:
        station_id = charger_to_station[charger_id]
        station_reports[station_id].append((start_time, end_time, is_up))

    # Calculate uptime for each station
    uptimes: Dict[int, int] = {}

    for station_id, charger_ids in stations.items():
        reports_for_station = station_reports[station_id]

        if not reports_for_station:
            # No reports for this station - undefined behavior
            # We'll set uptime to 0 since there's no data
            uptimes[station_id] = 0
            continue

        # Find the overall time period (min start to max end)
        min_start = min(start for start, end, is_up in reports_for_station)
        max_end = max(end for start, end, is_up in reports_for_station)
        total_time = max_end - min_start

        # Collect up intervals
        up_intervals: List[Tuple[int, int]] = []

        for start_time, end_time, is_up in reports_for_station:
            if is_up:
                up_intervals.append((start_time, end_time))

        # Merge up intervals to handle overlaps
        merged_up = merge_intervals(up_intervals)

        # Calculate up time
        up_time = calculate_total_time(merged_up)

        if total_time == 0:
            uptimes[station_id] = 0
        else:
            # Floor the percentage
            uptimes[station_id] = int((up_time * 100) // total_time)

    return uptimes


def main():
    if len(sys.argv) != 2:
        print("ERROR", file=sys.stdout)
        print("Usage: {} <input_file>".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        # Parse input file
        stations, reports = parse_input_file(input_file)

        # Calculate uptime for each station
        uptimes = calculate_station_uptime(stations, reports)

        # Output results in ascending station ID order
        for station_id in sorted(uptimes.keys()):
            print(f"{station_id} {uptimes[station_id]}")

    except ValueError as e:
        print("ERROR", file=sys.stdout)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("ERROR", file=sys.stdout)
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
