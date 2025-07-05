import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import { promisify } from 'util';

// 요청 바디의 타입 정의
interface CustomRecommendationRequest {
  mbti: string;
  interests: string[];
  channel_category: string;
  budget_level: string;
}

// Python 스크립트 실행을 위한 헬퍼 함수
function executePersonaEngine(userData: CustomRecommendationRequest): Promise<any> {
  return new Promise((resolve, reject) => {
    // Python 스크립트에 전달할 JSON 데이터를 준비
    const pythonScript = `
import sys
import json
import os
sys.path.append('${process.cwd()}')

from persona_recommendation_engine import PersonaRecommendationEngine

# 사용자 데이터
user_data = ${JSON.stringify(userData)}

try:
    # 엔진 초기화 (디버그 모드 활성화)
    engine = PersonaRecommendationEngine(debug_mode=True)
    
    # 맞춤 추천 생성
    result = engine.generate_custom_recommendation(user_data)
    
    # 결과를 JSON으로 출력
    print("RESULT_START")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("RESULT_END")
    
except Exception as e:
    print("ERROR_START")
    print(f"Error: {str(e)}")
    print("ERROR_END")
    sys.exit(1)
`;

    // Python 프로세스 실행
    const pythonProcess = spawn('python3', ['-c', pythonScript], {
      cwd: process.cwd(),
      env: { ...process.env, PYTHONPATH: process.cwd() }
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error('Python process error:', stderr);
        reject(new Error(`Python process exited with code ${code}: ${stderr}`));
        return;
      }

      try {
        // RESULT_START와 RESULT_END 사이의 JSON 추출
        const resultMatch = stdout.match(/RESULT_START\s*([\s\S]*?)\s*RESULT_END/);
        if (resultMatch) {
          const jsonResult = JSON.parse(resultMatch[1]);
          resolve(jsonResult);
        } else {
          console.error('Could not find result in output:', stdout);
          reject(new Error('Could not parse Python output'));
        }
      } catch (error) {
        console.error('JSON parsing error:', error);
        console.error('Raw output:', stdout);
        reject(new Error('Failed to parse Python output as JSON'));
      }
    });

    pythonProcess.on('error', (error) => {
      console.error('Failed to start Python process:', error);
      reject(new Error(`Failed to start Python process: ${error.message}`));
    });
  });
}

export async function POST(request: NextRequest) {
  try {
    // 요청 바디 파싱
    const body = await request.json() as CustomRecommendationRequest;
    
    // 입력 데이터 검증
    const { mbti, interests, channel_category, budget_level } = body;
    
    if (!mbti || !interests || !channel_category || !budget_level) {
      return NextResponse.json(
        { 
          error: 'Missing required fields', 
          details: 'mbti, interests, channel_category, and budget_level are required' 
        },
        { status: 400 }
      );
    }

    // MBTI 검증
    const validMBTI = ['INFJ', 'INFP', 'INTJ', 'INTP', 'ISFJ', 'ISFP', 'ISTJ', 'ISTP', 
                       'ENFJ', 'ENFP', 'ENTJ', 'ENTP', 'ESFJ', 'ESFP', 'ESTJ', 'ESTP'];
    if (!validMBTI.includes(mbti)) {
      return NextResponse.json(
        { error: 'Invalid MBTI type', details: `MBTI must be one of: ${validMBTI.join(', ')}` },
        { status: 400 }
      );
    }

    // 채널 카테고리 검증
    const validCategories = ['Tech', 'Fashion', 'Food/Travel', 'Beauty', 'Lifestyle'];
    if (!validCategories.includes(channel_category)) {
      return NextResponse.json(
        { error: 'Invalid channel category', details: `Category must be one of: ${validCategories.join(', ')}` },
        { status: 400 }
      );
    }

    // 예산 레벨 검증
    const validBudgets = ['low', 'medium', 'high'];
    if (!validBudgets.includes(budget_level)) {
      return NextResponse.json(
        { error: 'Invalid budget level', details: `Budget level must be one of: ${validBudgets.join(', ')}` },
        { status: 400 }
      );
    }

    // 관심사 배열 검증
    if (!Array.isArray(interests) || interests.length === 0) {
      return NextResponse.json(
        { error: 'Invalid interests', details: 'Interests must be a non-empty array of strings' },
        { status: 400 }
      );
    }

    console.log('Processing custom recommendation request:', {
      mbti,
      interests: interests.slice(0, 3), // 로그에는 처음 3개만 표시
      channel_category,
      budget_level
    });

    // PersonaRecommendationEngine 실행
    const recommendation = await executePersonaEngine(body);

    // 성공 응답
    return NextResponse.json({
      success: true,
      data: recommendation,
      meta: {
        processed_at: new Date().toISOString(),
        user_profile: {
          mbti,
          interests_count: interests.length,
          channel_category,
          budget_level
        }
      }
    }, { 
      status: 200,
      headers: {
        'Content-Type': 'application/json; charset=utf-8'
      }
    });

  } catch (error) {
    console.error('Custom recommendation API error:', error);
    
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        details: error instanceof Error ? error.message : 'Unknown error occurred',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}

// OPTIONS 메서드 지원 (CORS)
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
} 