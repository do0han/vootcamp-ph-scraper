'use client'

import { useState, useCallback } from 'react'
import { User, Heart, Briefcase, DollarSign, Sparkles, Loader2, Tag, X } from 'lucide-react'

export interface CustomRecommendationData {
  mbti: string
  interests: string[]
  channel_category: string
  budget_level: string
}

interface CustomRecommendationFormProps {
  onReportGenerated: (report: any) => void
}

const MBTI_OPTIONS = [
  { value: 'INFJ', label: 'INFJ - 선의의 옹호자', description: '내향적, 직관적, 감정적, 판단적' },
  { value: 'INFP', label: 'INFP - 중재자', description: '내향적, 직관적, 감정적, 인식적' },
  { value: 'INTJ', label: 'INTJ - 건축가', description: '내향적, 직관적, 사고적, 판단적' },
  { value: 'INTP', label: 'INTP - 논리술사', description: '내향적, 직관적, 사고적, 인식적' },
  { value: 'ISFJ', label: 'ISFJ - 수호자', description: '내향적, 감각적, 감정적, 판단적' },
  { value: 'ISFP', label: 'ISFP - 모험가', description: '내향적, 감각적, 감정적, 인식적' },
  { value: 'ISTJ', label: 'ISTJ - 현실주의자', description: '내향적, 감각적, 사고적, 판단적' },
  { value: 'ISTP', label: 'ISTP - 만능재주꾼', description: '내향적, 감각적, 사고적, 인식적' },
  { value: 'ENFJ', label: 'ENFJ - 선도자', description: '외향적, 직관적, 감정적, 판단적' },
  { value: 'ENFP', label: 'ENFP - 활동가', description: '외향적, 직관적, 감정적, 인식적' },
  { value: 'ENTJ', label: 'ENTJ - 통솔자', description: '외향적, 직관적, 사고적, 판단적' },
  { value: 'ENTP', label: 'ENTP - 변론가', description: '외향적, 직관적, 사고적, 인식적' },
  { value: 'ESFJ', label: 'ESFJ - 집정관', description: '외향적, 감각적, 감정적, 판단적' },
  { value: 'ESFP', label: 'ESFP - 연예인', description: '외향적, 감각적, 감정적, 인식적' },
  { value: 'ESTJ', label: 'ESTJ - 경영자', description: '외향적, 감각적, 사고적, 판단적' },
  { value: 'ESTP', label: 'ESTP - 사업가', description: '외향적, 감각적, 사고적, 인식적' }
]

const CHANNEL_CATEGORIES = [
  { value: 'Tech', label: '🔧 Tech', description: '기술, 가젯, 프로그래밍' },
  { value: 'Fashion', label: '👗 Fashion', description: '패션, 스타일, 액세서리' },
  { value: 'Food/Travel', label: '🍜 Food/Travel', description: '음식, 여행, 문화' },
  { value: 'Beauty', label: '💄 Beauty', description: '뷰티, 스킨케어, 메이크업' },
  { value: 'Lifestyle', label: '✨ Lifestyle', description: '일상, 라이프스타일, 인테리어' }
]

const BUDGET_LEVELS = [
  { value: 'low', label: '💰 Low (₱200-1,500)', description: '저예산 제품 중심' },
  { value: 'medium', label: '💳 Medium (₱1,000-5,000)', description: '중간 가격대 제품' },
  { value: 'high', label: '💎 High (₱3,000-15,000)', description: '프리미엄 제품' }
]

const POPULAR_INTERESTS = [
  'vintage camera', 'specialty coffee', 'book reviews', 'slow living',
  'sustainable fashion', 'workwear', 'korean fashion', 'accessories',
  'k-beauty', 'skincare', 'makeup', 'k-pop', 'k-drama', 'korean food',
  'fitness', 'yoga', 'mindfulness', 'plant-based', 'minimalism',
  'photography', 'art', 'music', 'gaming', 'tech gadgets'
]

export function CustomRecommendationForm({ onReportGenerated }: CustomRecommendationFormProps) {
  const [formData, setFormData] = useState<CustomRecommendationData>({
    mbti: '',
    interests: [],
    channel_category: '',
    budget_level: ''
  })
  const [currentInterest, setCurrentInterest] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAddInterest = useCallback((interest: string) => {
    const trimmedInterest = interest.trim()
    if (trimmedInterest && !formData.interests.includes(trimmedInterest)) {
      setFormData(prev => ({
        ...prev,
        interests: [...prev.interests, trimmedInterest]
      }))
    }
    setCurrentInterest('')
  }, [formData.interests])

  const handleRemoveInterest = useCallback((interest: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.filter(i => i !== interest)
    }))
  }, [])

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddInterest(currentInterest)
    }
  }, [currentInterest, handleAddInterest])

  const isFormValid = formData.mbti && formData.interests.length > 0 && formData.channel_category && formData.budget_level

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isFormValid) return

    setIsGenerating(true)
    setError(null)

    try {
      console.log('🚀 Submitting custom recommendation request:', formData)
      
      const response = await fetch('/api/recommendations/custom', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.details || result.error || 'Failed to generate recommendation')
      }

      console.log('✅ Received custom recommendation:', result)
      onReportGenerated(result.data)

    } catch (error) {
      console.error('💥 Error generating custom recommendation:', error)
      setError(error instanceof Error ? error.message : 'Unknown error occurred')
    } finally {
      setIsGenerating(false)
    }
  }, [formData, isFormValid, onReportGenerated])

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div className="text-center space-y-4">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full mb-4">
          <Sparkles className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          맞춤형 추천 받기
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          당신만의 MBTI, 관심사, 채널 유형을 입력하고 AI가 분석한 개인화된 제품 추천과 콘텐츠 아이디어를 받아보세요.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* MBTI Selection */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center space-x-3 mb-4">
            <User className="w-5 h-5 text-purple-500" />
            <h3 className="text-lg font-semibold text-gray-900">MBTI 성격유형</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {MBTI_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, mbti: option.value }))}
                className={`p-3 rounded-lg border-2 text-left transition-all ${
                  formData.mbti === option.value
                    ? 'border-purple-500 bg-purple-50 text-purple-700'
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                }`}
              >
                <div className="font-medium text-sm">{option.label}</div>
                <div className="text-xs text-gray-500 mt-1">{option.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Interests Input */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center space-x-3 mb-4">
            <Heart className="w-5 h-5 text-pink-500" />
            <h3 className="text-lg font-semibold text-gray-900">관심사</h3>
          </div>
          
          {/* Interest Input */}
          <div className="mb-4">
            <input
              type="text"
              value={currentInterest}
              onChange={(e) => setCurrentInterest(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="관심사를 입력하고 Enter를 누르세요 (예: vintage camera, k-beauty)"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 outline-none"
            />
          </div>

          {/* Popular Interests */}
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">인기 관심사 (클릭하여 추가):</p>
            <div className="flex flex-wrap gap-2">
              {POPULAR_INTERESTS.map((interest) => (
                <button
                  key={interest}
                  type="button"
                  onClick={() => handleAddInterest(interest)}
                  disabled={formData.interests.includes(interest)}
                  className={`px-3 py-1 rounded-full text-sm transition-colors ${
                    formData.interests.includes(interest)
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-pink-100 text-pink-700 hover:bg-pink-200'
                  }`}
                >
                  {interest}
                </button>
              ))}
            </div>
          </div>

          {/* Selected Interests */}
          {formData.interests.length > 0 && (
            <div>
              <p className="text-sm text-gray-600 mb-2">선택된 관심사:</p>
              <div className="flex flex-wrap gap-2">
                {formData.interests.map((interest) => (
                  <div
                    key={interest}
                    className="inline-flex items-center px-3 py-1 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full text-sm"
                  >
                    <Tag className="w-3 h-3 mr-1" />
                    {interest}
                    <button
                      type="button"
                      onClick={() => handleRemoveInterest(interest)}
                      className="ml-2 text-white hover:text-gray-200"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Channel Category */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center space-x-3 mb-4">
            <Briefcase className="w-5 h-5 text-blue-500" />
            <h3 className="text-lg font-semibold text-gray-900">채널 카테고리</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {CHANNEL_CATEGORIES.map((category) => (
              <button
                key={category.value}
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, channel_category: category.value }))}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  formData.channel_category === category.value
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                }`}
              >
                <div className="font-medium">{category.label}</div>
                <div className="text-sm text-gray-500 mt-1">{category.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Budget Level */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center space-x-3 mb-4">
            <DollarSign className="w-5 h-5 text-green-500" />
            <h3 className="text-lg font-semibold text-gray-900">예산 수준</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {BUDGET_LEVELS.map((budget) => (
              <button
                key={budget.value}
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, budget_level: budget.value }))}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  formData.budget_level === budget.value
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                }`}
              >
                <div className="font-medium">{budget.label}</div>
                <div className="text-sm text-gray-500 mt-1">{budget.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <div className="text-center">
          <button
            type="submit"
            disabled={!isFormValid || isGenerating}
            className={`inline-flex items-center px-8 py-4 rounded-xl font-semibold text-white transition-all ${
              !isFormValid || isGenerating
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 transform hover:scale-105'
            }`}
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                AI가 분석 중...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 mr-2" />
                맞춤 추천 받기
              </>
            )}
          </button>
          
          {!isFormValid && (
            <p className="text-sm text-gray-500 mt-2">
              모든 항목을 입력해주세요
            </p>
          )}
        </div>
      </form>
    </div>
  )
} 