#!/bin/bash

# Test commands for the File Extractor API
# Make sure your Flask server is running on http://localhost:5000
# Or update BASE_URL to match your server URL

BASE_URL="http://localhost:5000"

echo "=== Testing Root Endpoint ==="
curl -X GET "$BASE_URL/"

echo -e "\n\n=== Testing Health Endpoint ==="
curl -X GET "$BASE_URL/health"

echo -e "\n\n=== Testing /extract with GET (TXT file) ==="
curl -X GET "$BASE_URL/extract?url=https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

echo -e "\n\n=== Testing /extract with POST (JSON body - TXT file) ==="
curl -X POST "$BASE_URL/extract" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"}'

echo -e "\n\n=== Testing /extract with POST (JSON body - CSV file) ==="
curl -X POST "$BASE_URL/extract" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/data.csv"}'

echo -e "\n\n=== Testing /extract - Missing URL (should return error) ==="
curl -X GET "$BASE_URL/extract"

echo -e "\n\n=== Testing /extract - Invalid URL (should return error) ==="
curl -X GET "$BASE_URL/extract?url=https://invalid-url-that-does-not-exist-12345.com/file.pdf"
