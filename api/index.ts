import express, { Request, Response } from 'express';
import cors from 'cors';
import mammoth from 'mammoth';
import Papa from 'papaparse';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const pdfParse = require('pdf-parse');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Health check endpoint
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', message: 'File Extractor API is running' });
});

// Extract endpoint
app.post('/api/extract', async (req: Request, res: Response) => {
  try {
    const { fileUrl } = req.body;
    
    if (!fileUrl) {
      return res.status(400).json({ error: 'fileUrl is required' });
    }

    console.log('📥 Downloading:', fileUrl);

    const response = await fetch(fileUrl);
    if (!response.ok) {
      return res.status(500).json({ error: 'Failed to download file' });
    }

    const buffer = Buffer.from(await response.arrayBuffer());
    const lower = fileUrl.toLowerCase();
    let extracted: any = null;

    if (lower.endsWith('.pdf')) {
      console.log('✅ PDF detected');
      const parsed = await pdfParse(buffer);
      extracted = { type: 'pdf', text: parsed.text };
    } else if (lower.endsWith('.csv')) {
      const parsed = Papa.parse(buffer.toString('utf-8'), {
        header: true,
        skipEmptyLines: true,
      });
      extracted = { type: 'csv', rows: parsed.data };
    } else if (lower.endsWith('.txt')) {
      extracted = { type: 'txt', text: buffer.toString('utf-8') };
    } else if (lower.endsWith('.docx')) {
      const result = await mammoth.extractRawText({ buffer });
      extracted = { type: 'docx', text: result.value };
    } else {
      return res.status(400).json({ error: 'Unsupported file type' });
    }

    return res.json({ success: true, extracted });
  } catch (err: any) {
    console.error('❌ Extraction error:', err);
    return res.status(500).json({ error: err.message });
  }
});

export default app;
