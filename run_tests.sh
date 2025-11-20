#!/bin/bash

echo "======================================"
echo "Running Station Uptime Calculator Tests"
echo "======================================"

# Test 1
echo ""
echo "Test 1: input_1.txt"
echo "Expected:"
cat input_1_expected_stdout.txt
echo ""
echo "Actual:"
python3 station_uptime.py input_1.txt
echo ""

# Compare (strip trailing newlines)
actual1=$(python3 station_uptime.py input_1.txt)
expected1=$(cat input_1_expected_stdout.txt)
if [ "$actual1" = "$expected1" ]; then
    echo "TEST 1: PASSED"
else
    echo "TEST 1: FAILED"
fi

echo ""
echo "--------------------------------------"

# Test 2
echo ""
echo "Test 2: input_2.txt"
echo "Expected:"
cat input_2_expected_stdout.txt
echo ""
echo "Actual:"
python3 station_uptime.py input_2.txt
echo ""

# Compare (strip trailing newlines)
actual2=$(python3 station_uptime.py input_2.txt)
expected2=$(cat input_2_expected_stdout.txt)
if [ "$actual2" = "$expected2" ]; then
    echo "TEST 2: PASSED"
else
    echo "TEST 2: FAILED"
fi

echo ""
echo "======================================"
echo "Testing Error Handling"
echo "======================================"

# Test error case - no arguments
echo ""
echo "Test: No arguments"
python3 station_uptime.py 2>&1
echo ""

# Test error case - missing file
echo ""
echo "Test: Missing file"
python3 station_uptime.py nonexistent.txt 2>&1
echo ""

echo "======================================"
echo "All Tests Complete"
echo "======================================"