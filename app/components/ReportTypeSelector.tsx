'use client'

import { ChevronDown } from 'lucide-react'
import { useState } from 'react'

export interface ReportType {
  id: string
  name: string
  description: string
  icon: string
}

const REPORT_TYPES: ReportType[] = [
  {
    id: 'content_ideas',
    name: '콘텐츠 아이디어',
    description: '트렌딩 토픽 기반 콘텐츠 아이디어 5개',
    icon: '💡'
  },
  {
    id: 'trend_analysis',
    name: '트렌드 분석',
    description: '현재 인기 키워드와 트렌드 상세 분석',
    icon: '📈'
  },
  {
    id: 'monetization',
    name: '수익화 전략',
    description: '페르소나별 맞춤 수익화 방법과 전략',
    icon: '💰'
  },
  {
    id: 'competitor_analysis',
    name: '경쟁자 분석',
    description: '비슷한 크리에이터들의 성공 사례 분석',
    icon: '🔍'
  },
  {
    id: 'content_calendar',
    name: '콘텐츠 캘린더',
    description: '월간 콘텐츠 계획과 업로드 스케줄',
    icon: '📅'
  }
]

interface ReportTypeSelectorProps {
  selectedType: ReportType | null
  onSelect: (type: ReportType) => void
}

export function ReportTypeSelector({ selectedType, onSelect }: ReportTypeSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        리포트 유형
      </label>
      
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full px-4 py-3 text-left bg-white border border-gray-300 rounded-lg shadow-sm hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {selectedType ? (
                <>
                  <span className="text-lg">{selectedType.icon}</span>
                  <div>
                    <div className="font-medium text-gray-900">{selectedType.name}</div>
                    <div className="text-sm text-gray-500">{selectedType.description}</div>
                  </div>
                </>
              ) : (
                <span className="text-gray-500">리포트 유형을 선택하세요</span>
              )}
            </div>
            <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </div>
        </button>

        {isOpen && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
            <div className="py-1">
              {REPORT_TYPES.map((type) => (
                <button
                  key={type.id}
                  onClick={() => {
                    onSelect(type)
                    setIsOpen(false)
                  }}
                  className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                    selectedType?.id === type.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{type.icon}</span>
                    <div>
                      <div className="font-medium text-gray-900">{type.name}</div>
                      <div className="text-sm text-gray-500">{type.description}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}