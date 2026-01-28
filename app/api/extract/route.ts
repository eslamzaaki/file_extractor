import { NextResponse } from "next/server"

import pdf from "pdf-parse"
import mammoth from "mammoth"
import Papa from "papaparse"

export async function POST(req: Request) {
  try {
    const { fileUrl } = await req.json()

    if (!fileUrl) {
      return NextResponse.json(
        { error: "fileUrl is required" },
        { status: 400 }
      )
    }

    console.log("📥 Downloading:", fileUrl)

    // 1. Download file from URL
    const response = await fetch(fileUrl)

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to download file" },
        { status: 500 }
      )
    }

    // Convert file → Buffer
    const arrayBuffer = await response.arrayBuffer()
    const buffer = Buffer.from(arrayBuffer)

    const lower = fileUrl.toLowerCase()

    let extracted: any = null

    // 2. Extract based on file type
    if (lower.endsWith(".pdf")) {
      const parsed = await pdf(buffer)

      extracted = {
        type: "pdf",
        text: parsed.text,
      }
    }

    else if (lower.endsWith(".docx")) {
      const result = await mammoth.extractRawText({ buffer })

      extracted = {
        type: "docx",
        text: result.value,
      }
    }

    else if (lower.endsWith(".csv")) {
      const csvText = buffer.toString("utf-8")

      const parsed = Papa.parse(csvText, {
        header: true,
        skipEmptyLines: true,
      })

      extracted = {
        type: "csv",
        rows: parsed.data,
      }
    }

    else if (lower.endsWith(".txt")) {
      extracted = {
        type: "txt",
        text: buffer.toString("utf-8"),
      }
    }

    else {
      return NextResponse.json(
        { error: "Unsupported file type" },
        { status: 400 }
      )
    }

    // 3. Return extracted content
    return NextResponse.json({
      success: true,
      extracted,
    })
  }

  catch (err: any) {
    console.error("❌ Extraction error:", err.message)

    return NextResponse.json(
      { error: err.message },
      { status: 500 }
    )
  }
}
