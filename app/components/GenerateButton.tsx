'use client'

import { memo } from 'react'
import { Sparkles } from 'lucide-react'
import { Persona } from './PersonaSelector'

interface GenerateButtonProps {
  selectedPersona: Persona | null
  isGenerating: boolean
  onClick: () => void
}

function GenerateButtonComponent({ selectedPersona, isGenerating, onClick }: GenerateButtonProps) {
  const isDisabled = !selectedPersona || isGenerating

  return (
    <button
      onClick={onClick}
      disabled={isDisabled}
      className={`
        w-full py-4 px-6 rounded-lg font-semibold text-lg transition-all duration-200
        flex items-center justify-center space-x-2
        ${isDisabled
          ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
          : 'bg-gradient-to-r from-ph-blue to-indigo-600 text-white hover:from-ph-blue-600 hover:to-indigo-700 hover:shadow-lg transform hover:scale-[1.02]'
        }
      `}
    >
      {isGenerating ? (
        <>
          <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div>
          <span>콘텐츠 아이디어 생성 중...</span>
        </>
      ) : (
        <>
          <Sparkles className="w-5 h-5" />
          <span>
            {selectedPersona
              ? `${selectedPersona.name} 아이디어 생성하기`
              : '페르소나를 선택해주세요'
            }
          </span>
        </>
      )}
    </button>
  )
}

export const GenerateButton = memo(GenerateButtonComponent) 