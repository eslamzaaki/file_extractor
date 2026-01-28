# File Extractor Server

A Node.js Express server for extracting text content from various file types (PDF, CSV, TXT, DOCX) via URL.

## Features

- Extract text from PDF files
- Parse CSV files with headers
- Read plain text files
- Extract text from DOCX (Word) files
- RESTful API with Express.js
- TypeScript support
- CORS enabled

## Installation

```bash
npm install
```

## Development

Run the development server with hot reload:

```bash
npm run dev
```

The server will start on `http://localhost:3000`

## Production

Build the TypeScript code:

```bash
npm run build
```

Start the production server:

```bash
npm start
```

## API Endpoints

### POST `/api/extract`

Extract content from a file URL.

**Request Body:**
```json
{
  "fileUrl": "https://example.com/file.pdf"
}
```

**Success Response:**
```json
{
  "success": true,
  "extracted": {
    "type": "pdf",
    "text": "Extracted text content..."
  }
}
```

**Error Response:**
```json
{
  "error": "Error message"
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "File Extractor API is running"
}
```

## Supported File Types

- **PDF** (`.pdf`) - Extracts text using pdf-parse
- **CSV** (`.csv`) - Parses with headers using papaparse
- **TXT** (`.txt`) - Plain text extraction
- **DOCX** (`.docx`) - Extracts text using mammoth

## Example Usage

### Using curl

```bash
curl -X POST http://localhost:3000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"fileUrl": "https://example.com/file.pdf"}'
```

### Using fetch (JavaScript)

```javascript
const response = await fetch('http://localhost:3000/api/extract', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    fileUrl: 'https://example.com/file.pdf'
  })
});

const data = await response.json();
console.log(data);
```

## Project Structure

```
extractor-server/
├── server.ts          # Main Express server file
├── package.json       # Dependencies and scripts
├── tsconfig.json      # TypeScript configuration
├── public/            # Static files (test.html)
└── dist/              # Compiled JavaScript (generated)
```

## Technologies

- **Express.js** - Web framework
- **TypeScript** - Type safety
- **pdf-parse** - PDF text extraction
- **papaparse** - CSV parsing
- **mammoth** - DOCX text extraction
- **CORS** - Cross-origin resource sharing

## Deployment

### Deploy to Vercel

This Express server is configured for easy deployment to Vercel:

1. **Using Vercel CLI:**
   ```bash
   npm i -g vercel
   vercel
   ```

2. **Using GitHub:**
   - Push code to GitHub
   - Import repository in Vercel dashboard
   - Vercel will auto-detect and deploy

See [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md) for detailed deployment instructions.

### Configuration Files

- `vercel.json` - Vercel serverless function configuration
- `api/index.ts` - Serverless function entry point
- `server.ts` - Express app (works both locally and on Vercel)

## License

MIT
