#!/bin/bash
# Quick API Testing Script
# Usage: ./test_api.sh [base_url]
# Example: ./test_api.sh http://127.0.0.1:5000
# Example: ./test_api.sh https://your-app.onrender.com

BASE_URL="${1:-http://127.0.0.1:5000}"
echo "Testing API at: $BASE_URL"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s "$BASE_URL/health" | python -m json.tool
echo -e "\n"

# Test 2: Mark Attendance
echo "2. Testing Mark Attendance..."
curl -s -X POST "$BASE_URL/api/mark_attendance" \
  -H "Content-Type: application/json" \
  -d '{
    "faculty_id": "F001",
    "course_id": "CS101",
    "attendance_list": [
      {"enroll_no": "S1001", "status": "Present"},
      {"enroll_no": "S1002", "status": "Absent"}
    ]
  }' | python -m json.tool
echo -e "\n"

# Test 3: View Report for Student 1
echo "3. Testing View Report (S1001)..."
curl -s "$BASE_URL/api/report/S1001" | python -m json.tool
echo -e "\n"

# Test 4: View Report for Student 2
echo "4. Testing View Report (S1002)..."
curl -s "$BASE_URL/api/report/S1002" | python -m json.tool
echo -e "\n"

# Test 5: Error Case - Unauthorized Faculty
echo "5. Testing Error Case (Unauthorized Faculty)..."
curl -s -X POST "$BASE_URL/api/mark_attendance" \
  -H "Content-Type: application/json" \
  -d '{
    "faculty_id": "F999",
    "course_id": "CS101",
    "attendance_list": [
      {"enroll_no": "S1001", "status": "Present"}
    ]
  }' | python -m json.tool
echo -e "\n"

# Test 6: Error Case - Student Not Found
echo "6. Testing Error Case (Student Not Found)..."
curl -s "$BASE_URL/api/report/S9999" | python -m json.tool
echo -e "\n"

echo "=========================================="
echo "All tests completed!"

