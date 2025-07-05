import { NextResponse } from 'next/server'
import { spawn } from 'child_process'

interface GenerateRequest {
  persona: {
    id: string
    name: string
    emoji: string
  }
  reportType: {
    id: string
    name: string
  }
}

interface GenerateResponse {
  report?: string
  error?: string
}

async function callReportDispatcher(persona: any, reportType: any): Promise<string> {
  return new Promise((resolve, reject) => {
    const userProfile = {
      persona: persona,
      reportType: reportType
    }

    const python = spawn('python3', ['-c', `
import sys
sys.path.append('${process.cwd()}')
from report_dispatcher import generate_specialized_report
import json

user_profile = ${JSON.stringify(userProfile)}
report_type = "${reportType.id}"
result = generate_specialized_report(user_profile, report_type)
print(result)
`])

    let output = ''
    let error = ''

    python.stdout.on('data', (data) => {
      output += data.toString()
    })

    python.stderr.on('data', (data) => {
      error += data.toString()
    })

    python.on('close', (code) => {
      if (code === 0) {
        resolve(output.trim())
      } else {
        reject(new Error(`Python script failed with code ${code}: ${error}`))
      }
    })
  })
}

export async function POST(request: Request): Promise<NextResponse<GenerateResponse>> {
  try {
    const { persona, reportType } = await request.json() as GenerateRequest

    // Call the Python report dispatcher
    const report = await callReportDispatcher(persona, reportType)
    
    return NextResponse.json({ report })
  } catch (error) {
    console.error('Error generating report:', error)
    return NextResponse.json(
      { error: 'Failed to generate report' },
      { status: 500 }
    )
  }
}

// Also support GET requests for testing
export async function GET() {
  return NextResponse.json({
    message: 'Vootcamp PH Report Generator API',
    usage: 'POST /api/generate with { "persona_id": "lifestyle" | "entrepreneur" | "foodie" }',
    available_personas: ['lifestyle', 'entrepreneur', 'foodie', 'tech', 'fitness', 'education']
  })
} 