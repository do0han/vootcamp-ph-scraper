import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

// Simple in-memory cache for demonstration
const cache = new Map<string, { data: string, timestamp: number }>()
const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

interface GenerateRequest {
  persona_id: string
  report_type?: string
}

interface GenerateResponse {
  report?: string
  error?: string
}

export async function POST(request: NextRequest): Promise<NextResponse<GenerateResponse>> {
  try {
    const body: GenerateRequest = await request.json()
    const { persona_id, report_type = 'content_ideas' } = body

    if (!persona_id) {
      return NextResponse.json(
        { error: 'persona_id is required' },
        { status: 400 }
      )
    }

    // Check cache first
    const cacheKey = `${persona_id}-${report_type}`
    const cached = cache.get(cacheKey)
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      console.log(`🚀 Cache hit for ${cacheKey}`)
      return NextResponse.json({ report: cached.data })
    }

    // Map frontend persona IDs to backend persona names
    const personaMapping: Record<string, string> = {
      'lifestyle': 'zaila_mae',
      'entrepreneur': 'alex_entrepreneur',
      'foodie': 'zaila_mae', // Use zaila_mae for food/travel content
      'tech': 'just_elias', // Use just_elias for tech content
      'fitness': 'zaila_mae', // Use zaila_mae for fitness/health content
      'education': 'just_elias', // Use just_elias for educational content
    }

    const backendPersonaName = personaMapping[persona_id]
    if (!backendPersonaName) {
      return NextResponse.json(
        { error: `Unknown persona_id: ${persona_id}` },
        { status: 400 }
      )
    }

    console.log(`🎯 Generating report for persona: ${persona_id} -> ${backendPersonaName}`)

    // Execute Python script
    const report = await executePersonaScript(backendPersonaName)
    
    if (!report) {
      return NextResponse.json(
        { error: 'Failed to generate report - empty response' },
        { status: 500 }
      )
    }

    console.log(`✅ Successfully generated report for ${persona_id}`)
    
    // Cache the result
    cache.set(cacheKey, { data: report, timestamp: Date.now() })
    
    return NextResponse.json({ report })

  } catch (error) {
    console.error('💥 Error in generate API:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    )
  }
}

async function executePersonaScript(personaName: string): Promise<string> {
  return new Promise((resolve, reject) => {
    // Get the project root directory
    const projectRoot = process.cwd()
    const pythonScriptPath = path.join(projectRoot, 'main.py')

    console.log(`🐍 Executing: python ${pythonScriptPath} --run-for ${personaName} --api-mode`)

    // Spawn Python process
    const pythonProcess = spawn('python', [pythonScriptPath, '--run-for', personaName, '--api-mode'], {
      cwd: projectRoot,
      stdio: ['pipe', 'pipe', 'pipe'], // stdin, stdout, stderr
    })

    let stdout = ''
    let stderr = ''

    // Capture stdout (the report)
    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    // Capture stderr (logs and errors)
    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    // Handle process completion
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        // Success - return the report from stdout
        const trimmedReport = stdout.trim()
        if (trimmedReport) {
          console.log(`✅ Python script completed successfully`)
          console.log(`📊 Report length: ${trimmedReport.length} characters`)
          resolve(trimmedReport)
        } else {
          console.error('❌ Python script completed but returned empty report')
          console.error('Stderr:', stderr)
          reject(new Error('Python script returned empty report'))
        }
      } else {
        console.error(`❌ Python script failed with exit code: ${code}`)
        console.error('Stderr:', stderr)
        reject(new Error(`Python script failed with exit code ${code}: ${stderr}`))
      }
    })

    // Handle process errors
    pythonProcess.on('error', (error) => {
      console.error('💥 Failed to start Python process:', error)
      reject(new Error(`Failed to start Python process: ${error.message}`))
    })

    // Set a timeout (30 seconds)
    const timeout = setTimeout(() => {
      pythonProcess.kill('SIGTERM')
      reject(new Error('Python script execution timed out after 30 seconds'))
    }, 30000)

    // Clear timeout on successful completion
    pythonProcess.on('close', () => {
      clearTimeout(timeout)
    })
  })
}

// Also support GET requests for testing
export async function GET() {
  return NextResponse.json({
    message: 'Vootcamp PH Report Generator API',
    usage: 'POST /api/generate with { "persona_id": "lifestyle" | "entrepreneur" | "foodie" }',
    available_personas: ['lifestyle', 'entrepreneur', 'foodie', 'tech', 'fitness', 'education']
  })
} 