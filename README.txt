================================================================================
                           FILES INCLUDED
================================================================================

1. station_uptime.py        - Main solution (Python 3 script)
2. SUBMISSION_README.txt    - This file (instructions and explanations)
3. test_station_uptime.py   - Unit tests (pytest)
4. run_tests.sh             - Integration test script

================================================================================
                    HOW TO RUN THE SOLUTION
================================================================================

PREREQUISITES:
- Python 3.6 or higher (tested with Python 3.8+)
- Linux environment with amd64 architecture (or any POSIX-compliant system)

EXECUTION:
    python3 station_uptime.py <path_to_input_file>

    OR (if file is executable):

    chmod +x station_uptime.py
    ./station_uptime.py <path_to_input_file>

EXAMPLES:
    python3 station_uptime.py input_1.txt
    python3 station_uptime.py /path/to/test/data.txt

================================================================================
                        OUTPUT FORMAT
================================================================================

On SUCCESS:
    <Station_ID_1> <Uptime_Percentage>
    <Station_ID_2> <Uptime_Percentage>
    ...

    - Station IDs are sorted in ascending order
    - Uptime percentages are integers [0-100], floored to nearest percent

On ERROR:
    ERROR

    - Prints "ERROR" to stdout
    - Detailed error message printed to stderr

================================================================================
                    DESIGN DECISIONS & AMBIGUITY RESOLUTIONS
================================================================================

1. TOTAL TIME PERIOD CALCULATION:
   - The "entire time period that any charger at that station was reporting in"
     is interpreted as the span from the MINIMUM start time to the MAXIMUM end
     time across all reports for that station.
   - Gaps between reports count as downtime (as specified in the problem).

2. MULTIPLE CHARGERS AT A STATION:
   - If ANY charger at a station is "up" during a time interval, the station
     is considered "up" during that interval.
   - Overlapping "up" intervals from multiple chargers are merged to avoid
     double-counting.

3. NO REPORTS FOR A STATION:
   - If a station is defined but has no charger reports, uptime is set to 0%.
   - This is an edge case not explicitly defined in the problem.

4. OVERLAPPING TIME INTERVALS:
   - Overlapping "up" intervals are merged using interval merging algorithm.
   - Example: Intervals [0, 50] and [25, 75] merge to [0, 75].

5. FLOOR ROUNDING:
   - Uptime percentage is always floored (rounded down) as specified.
   - Example: 66.67% becomes 66%.

6. INPUT VALIDATION:
   - All preconditions are validated (uint32 for IDs, uint64 for times).
   - Invalid inputs result in "ERROR" output.
   - Duplicate station IDs or charger IDs are rejected.
   - Reports referencing unknown charger IDs are rejected.

7. EMPTY TIME PERIODS:
   - If start_time >= end_time in a report, it's considered invalid.
   - This prevents division by zero and logical errors.

================================================================================
                       ALGORITHM COMPLEXITY
================================================================================

Time Complexity: O(R log R)
- Where R is the number of reports
- Dominated by sorting intervals for merging

Space Complexity: O(R + S)
- R for storing reports
- S for storing station mappings

The algorithm scales well with large datasets as interval merging is efficient.

================================================================================
                          ERROR HANDLING
================================================================================

The program handles the following error cases:
- Missing or unreadable input file
- Missing command-line argument
- Invalid section structure (data before section header)
- Missing required sections
- Invalid integer formats
- Out-of-range values (uint32/uint64 violations)
- Invalid boolean values (must be "true" or "false")
- Invalid time ranges (start >= end)
- Duplicate station or charger IDs
- References to undefined charger IDs

================================================================================
                           TESTING
================================================================================

UNIT TESTS (pytest):
    pip3 install pytest
    pytest test_station_uptime.py -v

    Tests cover:
    - Interval merging algorithm
    - Uptime calculation logic
    - Input parsing and validation
    - Error handling for invalid inputs
    - Edge cases and boundary conditions
    - Both example input files

INTEGRATION TESTS (bash script):
    chmod +x run_tests.sh
    ./run_tests.sh

    Runs the solution against provided test inputs and compares with
    expected outputs.

MANUAL TESTING:
    python3 station_uptime.py input_1.txt
    python3 station_uptime.py input_2.txt

Expected outputs:
- input_1.txt: 0 100, 1 0, 2 75
- input_2.txt: 0 66, 1 100

================================================================================
