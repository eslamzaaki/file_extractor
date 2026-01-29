# Curl Commands to Test the File Extractor API

## Prerequisites
Make sure your Flask server is running:
```bash
python app.py
# or
flask run
```

The server should be running on `http://localhost:5000` by default.

## Basic Endpoints

### 1. Root Endpoint (API Information)
```bash
curl -X GET http://localhost:5000/
```

### 2. Health Check Endpoint
```bash
curl -X GET http://localhost:5000/health
```

## Extract Endpoint - GET Method

### Extract from TXT file (using query parameter)
```bash
curl -X GET "http://localhost:5000/extract?url=https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
```

### Extract from CSV file
```bash
curl -X GET "http://localhost:5000/extract?url=https://raw.githubusercontent.com/datasets/covid-19/main/data/time-series-19-covid-combined.csv"
```

### Extract from a text file
```bash
curl -X GET "http://localhost:5000/extract?url=https://www.gutenberg.org/files/1342/1342-0.txt"
```

## Extract Endpoint - POST Method

### Extract from PDF (JSON body)
```bash
curl -X POST http://localhost:5000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"}'
```

### Extract from CSV (JSON body)
```bash
curl -X POST http://localhost:5000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://raw.githubusercontent.com/datasets/covid-19/main/data/time-series-19-covid-combined.csv"}'
```

### Extract from DOCX file
```bash
curl -X POST http://localhost:5000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/document.docx"}'
```

## Error Cases

### Missing URL parameter
```bash
curl -X GET http://localhost:5000/extract
```

### Invalid URL
```bash
curl -X GET "http://localhost:5000/extract?url=https://invalid-url-that-does-not-exist-12345.com/file.pdf"
```

### Unsupported file type
```bash
curl -X GET "http://localhost:5000/extract?url=https://example.com/file.exe"
```

## Pretty Print JSON Output

Add `| python -m json.tool` or `| jq` for formatted output:

```bash
curl -X GET "http://localhost:5000/extract?url=https://example.com/file.txt" | python -m json.tool
```

Or with jq (if installed):
```bash
curl -X GET "http://localhost:5000/extract?url=https://example.com/file.txt" | jq
```

## Testing with Local Files

If you want to test with a local file, you'll need to serve it first. You can use Python's HTTP server:

```bash
# In a separate terminal, serve files from a directory
python -m http.server 8000

# Then test with the local file
curl -X GET "http://localhost:5000/extract?url=http://localhost:8000/your-file.pdf"
```

## Example Response

Successful extraction:
```json
{
  "success": true,
  "content": "Extracted text content here...",
  "file_type": ".txt",
  "content_length": 1234
}
```

Error response:
```json
{
  "error": "Missing file URL. Provide \"url\" parameter in query string (GET) or JSON body (POST)"
}
```
