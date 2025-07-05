'use client'

import { useState } from 'react'
import { PersonaSelector } from './components/PersonaSelector'
import { GenerateButton } from './components/GenerateButton'
import { ReportDisplay } from './components/ReportDisplay'
import { LoadingState } from './components/LoadingState'
import { PremiumHint } from './components/PremiumHint'
import { ReportHistory } from './components/ReportHistory'
import { ReportTypeSelector, ReportType } from './components/ReportTypeSelector'
import { Crown, Sparkles, Save } from 'lucide-react'

export interface Persona {
  id: string
  name: string
  description: string
  emoji: string
  color: string
}

const PERSONAS: Persona[] = [
  {
    id: 'lifestyle',
    name: 'Lifestyle Creator',
    description: '일상, 패션, 뷰티 콘텐츠로 영감을 주는 크리에이터',
    emoji: '✨',
    color: 'from-pink-400 to-purple-500'
  },
  {
    id: 'entrepreneur', 
    name: 'Business Entrepreneur',
    description: '비즈니스 팁과 창업 스토리를 공유하는 크리에이터',
    emoji: '💼',
    color: 'from-blue-400 to-indigo-500'
  },
  {
    id: 'foodie',
    name: 'Food & Travel',
    description: '맛집 탐방과 여행 경험을 공유하는 크리에이터',
    emoji: '🍜',
    color: 'from-orange-400 to-red-500'
  },
  {
    id: 'tech',
    name: 'Tech Reviewer',
    description: '최신 기술과 가젯 리뷰를 제공하는 크리에이터',
    emoji: '📱',
    color: 'from-gray-400 to-slate-600'
  },
  {
    id: 'fitness',
    name: 'Fitness Coach',
    description: '운동과 건강한 라이프스타일을 알려주는 크리에이터',
    emoji: '💪',
    color: 'from-green-400 to-emerald-500'
  },
  {
    id: 'education',
    name: 'Educational Content',
    description: '학습과 교육 콘텐츠를 만드는 크리에이터',
    emoji: '📚',
    color: 'from-yellow-400 to-amber-500'
  }
]

const SAMPLE_REPORT = `# 🎬 콘텐츠 아이디어 리포트: Lifestyle Creator

## 📊 트렌드 분석

### 현재 인기 토픽
- **"Day in My Life" 콘텐츠** - 조회수 평균 15% 증가
- **지속가능한 라이프스타일** - 환경친화적 제품 리뷰
- **홈 인테리어 & 데코** - 작은 공간 활용 팁

### 계절별 추천 키워드
- 🌺 **봄 시즌**: 체리 블라썸 룩북, 봄맞이 클리닝
- ☀️ **여름 준비**: 비치웨어 하울, 썸머 스킨케어 루틴

## 💡 콘텐츠 아이디어 (Top 5)

### 1. "필리핀 전통 패브릭으로 모던 룩 만들기"
- **형식**: 패션 룩북 + 스타일링 팁
- **예상 조회수**: 25K-50K
- **최적 업로드 시간**: 금요일 오후 6-8시

### 2. "1만원으로 집 꾸미기 챌린지"
- **형식**: DIY 홈 데코 튜토리얼
- **타겟 키워드**: #BudgetDecor #DIYHome #PhilippineHome
- **예상 조회수**: 30K-60K

### 3. "로컬 브랜드 vs 글로벌 브랜드 비교 리뷰"
- **형식**: 정직한 제품 비교 리뷰
- **수익화 기회**: 제휴 링크, 브랜드 협업
- **예상 조회수**: 20K-40K

### 4. "Morning Routine: 바쁜 직장인 편"
- **형식**: 일상 브이로그
- **포함 요소**: 스킨케어, 간단 메이크업, 아침식사
- **예상 조회수**: 35K-70K

### 5. "필리핀 로컬 카페 투어"
- **형식**: 여행/맛집 브이로그
- **콜라보 기회**: 카페 사장과의 인터뷰
- **예상 조회수**: 40K-80K

## 💰 수익화 전략

### 즉시 적용 가능
1. **제휴 마케팅**: 패션, 뷰티 제품 링크
2. **브랜드 협업**: 로컬 브랜드와의 파트너십
3. **스폰서십**: 홈 데코, 라이프스타일 브랜드

### 장기 전략
- **자체 제품 런칭**: 라이프스타일 플래너, 디지털 가이드
- **온라인 코스**: 스타일링 클래스, 홈 데코 워크숍
- **멤버십**: 독점 콘텐츠, 개인 상담

## 📈 성과 최적화 팁

### 썸네일 최적화
- **밝고 선명한 색상** 사용
- **얼굴 노출** (클릭률 30% 증가)
- **텍스트 오버레이** (핵심 키워드 포함)

### 업로드 타이밍
- **최적 시간**: 화-목 오후 6-9시
- **주말**: 오전 10-12시 (브런치 콘텐츠)

### 인게이지먼트 전략
- **첫 24시간이 중요**: 적극적인 댓글 응답
- **스토리 활용**: 비하인드 콘텐츠 공유
- **커뮤니티 구축**: 정기적인 Q&A 세션

---

*✨ 이 리포트는 AI가 최신 트렌드 데이터를 분석하여 생성했습니다.*`

export default function HomePage() {
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null)
  const [selectedReportType, setSelectedReportType] = useState<ReportType | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [report, setReport] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!selectedPersona) return
    
    setIsGenerating(true)
    setReport(null)
    
    try {
      console.log(`🎯 Generating ${selectedReportType?.name || 'default'} report for persona: ${selectedPersona.id}`)
      
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          persona_id: selectedPersona.id,
          report_type: selectedReportType?.id || 'content_ideas'
        })
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`)
      }
      
      if (data.report) {
        console.log(`✅ Successfully received report (${data.report.length} characters)`)
        setReport(data.report)
        
        // Save to history
        if (typeof window !== 'undefined' && (window as any).saveReport) {
          (window as any).saveReport(selectedPersona.name, selectedPersona.emoji, data.report)
        }
      } else {
        throw new Error('No report received from API')
      }
      
    } catch (error) {
      console.error('💥 Error generating report:', error)
      
      // Fallback to sample report in case of error
      console.log('📄 Falling back to sample report')
      setReport(SAMPLE_REPORT)
      
      // Save sample report to history too
      if (typeof window !== 'undefined' && (window as any).saveReport) {
        (window as any).saveReport(selectedPersona.name, selectedPersona.emoji, SAMPLE_REPORT)
      }
      
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSaveReport = () => {
    if (report && selectedPersona && typeof window !== 'undefined' && (window as any).saveReport) {
      (window as any).saveReport(selectedPersona.name, selectedPersona.emoji, report)
      // TODO: Show success toast
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 gradient-bg rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Vootcamp PH</h1>
                <p className="text-sm text-gray-500">AI 콘텐츠 아이디어 생성기</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <ReportHistory onLoadReport={setReport} />
              <PremiumHint />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Input */}
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                당신의 페르소나를 선택하세요
              </h2>
              <p className="text-gray-600">
                선택한 페르소나에 맞는 맞춤형 콘텐츠 아이디어를 생성해드립니다.
              </p>
            </div>

            <PersonaSelector
              personas={PERSONAS}
              selectedPersona={selectedPersona}
              onSelect={setSelectedPersona}
            />

            <ReportTypeSelector
              selectedType={selectedReportType}
              onSelect={setSelectedReportType}
            />

            <GenerateButton
              selectedPersona={selectedPersona}
              isGenerating={isGenerating}
              onClick={handleGenerate}
            />

            {/* Premium Features Preview */}
            <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg p-4 border border-amber-200">
              <div className="flex items-center space-x-2 mb-2">
                <Crown className="w-4 h-4 text-amber-600" />
                <span className="text-sm font-medium text-amber-800">Ka-Tropa Plan 미리보기</span>
              </div>
              <ul className="text-sm text-amber-700 space-y-1">
                <li>• 무제한 리포트 생성</li>
                <li>• 실시간 트렌드 분석</li>
                <li>• 자동 어필리에이트 링크 생성</li>
                <li>• 개인 맞춤 콘텐츠 캘린더</li>
              </ul>
            </div>
          </div>

          {/* Right Column - Output */}
          <div className="space-y-6">
            {!selectedPersona && !isGenerating && !report && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  콘텐츠 아이디어를 생성해보세요
                </h3>
                <p className="text-gray-500">
                  페르소나를 선택하고 생성 버튼을 클릭하면<br />
                  AI가 맞춤형 콘텐츠 아이디어를 제공합니다.
                </p>
              </div>
            )}

            {isGenerating && <LoadingState />}

            {report && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">생성된 리포트</h3>
                  <button
                    onClick={handleSaveReport}
                    className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <Save className="w-4 h-4" />
                    <span>저장</span>
                  </button>
                </div>
                <ReportDisplay 
                  report={report} 
                />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
} 