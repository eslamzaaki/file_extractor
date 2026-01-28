# API Testing Guide

## Endpoint
`POST https://file-extractor-3mgo.vercel.app/api/extract`

## Request Format
```json
{
  "fileUrl": "https://example.com/file.pdf"
}
```

## Test Examples

### 1. Test PDF File
```bash
curl -X POST https://file-extractor-3mgo.vercel.app/api/extract \
  -H "Content-Type: application/json" \
  -d "{\"fileUrl\": \"https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf\"}"
```

### 2. Test CSV File
```bash
curl -X POST https://file-extractor-3mgo.vercel.app/api/extract \
  -H "Content-Type: application/json" \
  -d "{\"fileUrl\": \"https://example.com/data.csv\"}"
```

### 3. Test TXT File
```bash
curl -X POST https://file-extractor-3mgo.vercel.app/api/extract \
  -H "Content-Type: application/json" \
  -d "{\"fileUrl\": \"https://www.learningcontainer.com/wp-content/uploads/2020/04/sample-text-file.txt\"}"
```

### 4. Test DOCX File
```bash
curl -X POST https://file-extractor-3mgo.vercel.app/api/extract \
  -H "Content-Type: application/json" \
  -d "{\"fileUrl\": \"https://example.com/document.docx\"}"
```

## Using Browser Console (JavaScript)

Open browser console (F12) and run:

```javascript
// Test PDF
fetch('https://file-extractor-3mgo.vercel.app/api/extract', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    fileUrl: 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
  })
})
.then(res => res.json())
.then(data => console.log(data))
.catch(err => console.error('Error:', err));
```

## Expected Response Format

### Success Response
```json
{
  "success": true,
  "extracted": {
    "type": "pdf",
    "text": "Extracted text content..."
  }
}
```

### Error Response
```json
{
  "error": "Error message here"
}
```

## Supported File Types
- PDF (.pdf)
- CSV (.csv)
- TXT (.txt)
- DOCX (.docx)
