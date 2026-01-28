export const runtime = "nodejs"  // ← must be first line

import { NextResponse } from "next/server"
import mammoth from "mammoth"
import Papa from "papaparse"
import { createRequire } from "module"

const require = createRequire(import.meta.url)
const pdfParse = require("pdf-parse")

export async function POST(req: Request) {
  try {
    const { fileUrl } = await req.json()
    if (!fileUrl) return NextResponse.json({ error: "fileUrl is required" }, { status: 400 })

    console.log("📥 Downloading:", fileUrl)

    const response = await fetch(fileUrl)
    if (!response.ok) return NextResponse.json({ error: "Failed to download file" }, { status: 500 })

    const buffer = Buffer.from(await response.arrayBuffer())
    const lower = fileUrl.toLowerCase()
    let extracted: any = null

    if (lower.endsWith(".pdf")) {
      console.log("✅ PDF detected")
      const parsed = await pdfParse(buffer)
      extracted = { type: "pdf", text: parsed.text }
    }
    else if (lower.endsWith(".csv")) {
      const parsed = Papa.parse(buffer.toString("utf-8"), { header: true, skipEmptyLines: true })
      extracted = { type: "csv", rows: parsed.data }
    }
    else if (lower.endsWith(".txt")) {
      extracted = { type: "txt", text: buffer.toString("utf-8") }
    }
    else if (lower.endsWith(".docx")) {
      const result = await mammoth.extractRawText({ buffer })
      extracted = { type: "docx", text: result.value }
    }
    else return NextResponse.json({ error: "Unsupported file type" }, { status: 400 })

    return NextResponse.json({ success: true, extracted })
  }
  catch (err: any) {
    console.error("❌ Extraction error:", err)
    return NextResponse.json({ error: err.message }, { status: 500 })
  }
}
