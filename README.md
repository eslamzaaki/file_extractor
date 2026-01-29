# File Extractor API

A simple Flask REST API that extracts text content from files (PDF, DOC, DOCX, CSV, TXT) via URL.

## Features

- Extract text content from PDF files
- Extract text content from DOC and DOCX files
- Extract content from CSV files
- Extract content from TXT files
- Support for both GET and POST requests
- Automatic file type detection

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd extractor-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

### Development Mode
```bash
python app.py
```

The server will start on `http://localhost:5000`

### Production Mode (with Gunicorn)
```bash
gunicorn app:app
```

## API Endpoints

### 1. Root Endpoint
Get API information:
```bash
GET /
```

### 2. Health Check
Check server status and supported formats:
```bash
GET /health
```

### 3. Extract Content
Extract content from a file URL:

**GET Request:**
```bash
GET /extract?url=<file_url>
```

**POST Request:**
```bash
POST /extract
Content-Type: application/json

{
  "url": "<file_url>"
}
```

## Usage Examples

### Extract from PDF (GET)
```bash
curl -X GET "http://localhost:5000/extract?url=https://example.com/document.pdf"
```

### Extract from CSV (POST)
```bash
curl -X POST http://localhost:5000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/data.csv"}'
```

### Extract from TXT file
```bash
curl -X GET "http://localhost:5000/extract?url=https://example.com/file.txt"
```

### Extract from DOCX file
```bash
curl -X POST http://localhost:5000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/document.docx"}'
```

## Response Format

### Success Response
```json
{
  "success": true,
  "content": "Extracted text content here...",
  "file_type": ".pdf",
  "content_length": 1234
}
```

### Error Response
```json
{
  "error": "Error message here"
}
```

## Supported File Types

- **PDF** (`.pdf`) - Extracts text using PyPDF2
- **DOCX** (`.docx`) - Extracts text using python-docx
- **DOC** (`.doc`) - Extracts text using docx2python
- **CSV** (`.csv`) - Extracts all rows as text
- **TXT** (`.txt`) - Extracts plain text content

## Testing

Run the test suite:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

## Deployment to Render

This project includes a `render.yaml` configuration file for easy deployment to Render.

1. Push your code to GitHub/GitLab
2. In Render dashboard, create a new Web Service
3. Connect your repository
4. Render will automatically detect the `render.yaml` file
5. The service will be deployed automatically

The `render.yaml` file configures:
- Python environment
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Free tier plan

## Environment Variables

- `PORT` - Server port (default: 5000)

## Error Handling

The API handles various error cases:
- Missing URL parameter
- Invalid or unreachable URLs
- Unsupported file types
- Extraction failures
- HTTP errors (404, 500, etc.)

## Example with Python

```python
import requests

# Extract content from a file URL
response = requests.post(
    'http://localhost:5000/extract',
    json={'url': 'https://example.com/document.pdf'}
)

if response.status_code == 200:
    data = response.json()
    print(f"File type: {data['file_type']}")
    print(f"Content length: {data['content_length']}")
    print(f"Content:\n{data['content']}")
else:
    print(f"Error: {response.json()['error']}")
```

## Example with JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

async function extractFile(url) {
  const response = await fetch('http://localhost:5000/extract', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url: url })
  });

  const data = await response.json();
  
  if (data.success) {
    console.log('File type:', data.file_type);
    console.log('Content:', data.content);
  } else {
    console.error('Error:', data.error);
  }
}

extractFile('https://example.com/document.pdf');
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
