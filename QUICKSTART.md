# Quick Start Guide

## Converted from Next.js to Express.js

This project has been successfully converted from a Next.js application to a Node.js Express server.

## Running the Server

### Development Mode (with hot reload)
```bash
npm run dev
```

### Production Mode
```bash
# Build TypeScript
npm run build

# Start server
npm start
```

## Testing the API

Once the server is running on `http://localhost:3000`, you can test it:

### Health Check
```bash
curl http://localhost:3000/health
```

### Extract File
```bash
curl -X POST http://localhost:3000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"fileUrl": "https://www.learningcontainer.com/wp-content/uploads/2020/04/sample-text-file.txt"}'
```

### Using the Test Page
Open `http://localhost:3000/test.html` in your browser for a visual testing interface.

## What Changed

- ✅ Converted Next.js API route to Express.js routes
- ✅ Updated dependencies (removed Next.js, React; added Express, CORS)
- ✅ Updated TypeScript configuration for Node.js
- ✅ Updated build scripts
- ✅ Added health check endpoint
- ✅ Static file serving for public directory
- ✅ CORS enabled for cross-origin requests

## Project Structure

```
extractor-server/
├── server.ts          # Express server (main file)
├── package.json       # Dependencies
├── tsconfig.json      # TypeScript config
├── dist/              # Compiled JavaScript (generated)
├── public/            # Static files
└── README.md          # Full documentation
```

## Environment Variables

You can set the port using:
```bash
PORT=3000 npm start
```

Default port is 3000.
