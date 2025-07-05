'use client'

import { useState } from 'react'
import { Clock, User, TrendingUp, ShoppingBag, Lightbulb, ExternalLink, Copy, Check } from 'lucide-react'

interface CustomRecommendationDisplayProps {
  data: {
    generated_at: string
    user_profile: {
      mbti: string
      interests: string[]
      channel_category: string
      budget_level: string
      persona_name: string
    }
    statistics: {
      total_products: number
      average_score: number
      high_score_products: number
      content_ideas_count: number
    }
    product_recommendations: Array<{
      product: string
      category: string
      price: string
      reason: string
      trending_score: number
      where_to_buy: string[]
      content_angle: string
    }>
    content_ideas: Array<{
      title: string
      type: string
      platform: string
      hook: string
      key_points: string[]
      call_to_action: string
    }>
  }
}

export function CustomRecommendationDisplay({ data }: CustomRecommendationDisplayProps) {
  const [copiedProduct, setCopiedProduct] = useState<string | null>(null)

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100'
    if (score >= 60) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const copyToClipboard = (text: string, productName: string) => {
    navigator.clipboard.writeText(text)
    setCopiedProduct(productName)
    setTimeout(() => setCopiedProduct(null), 2000)
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full mb-4">
          <User className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          맞춤형 추천 결과
        </h1>
        <p className="text-gray-600 flex items-center justify-center space-x-2">
          <Clock className="w-4 h-4" />
          <span>{formatDate(data.generated_at)}</span>
        </p>
      </div>

      {/* User Profile Summary */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <User className="w-5 h-5 mr-2 text-purple-600" />
          프로필 요약
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg">
            <div className="text-sm text-gray-600">MBTI</div>
            <div className="font-semibold text-purple-700">{data.user_profile.mbti}</div>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <div className="text-sm text-gray-600">채널 카테고리</div>
            <div className="font-semibold text-blue-700">{data.user_profile.channel_category}</div>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <div className="text-sm text-gray-600">예산 수준</div>
            <div className="font-semibold text-green-700 capitalize">{data.user_profile.budget_level}</div>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <div className="text-sm text-gray-600">관심사 개수</div>
            <div className="font-semibold text-pink-700">{data.user_profile.interests.length}개</div>
          </div>
        </div>
        
        {/* Interests */}
        <div className="mt-4">
          <div className="text-sm text-gray-600 mb-2">관심사:</div>
          <div className="flex flex-wrap gap-2">
            {data.user_profile.interests.map((interest) => (
              <span
                key={interest}
                className="px-3 py-1 bg-white text-purple-700 rounded-full text-sm border border-purple-200"
              >
                {interest}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-6 border border-gray-200 text-center">
          <ShoppingBag className="w-8 h-8 text-blue-500 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">{data.statistics.total_products}</div>
          <div className="text-sm text-gray-600">추천 제품</div>
        </div>
        <div className="bg-white rounded-xl p-6 border border-gray-200 text-center">
          <TrendingUp className="w-8 h-8 text-green-500 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">{data.statistics.average_score}</div>
          <div className="text-sm text-gray-600">평균 점수</div>
        </div>
        <div className="bg-white rounded-xl p-6 border border-gray-200 text-center">
          <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center mx-auto mb-2">
            <span className="text-white font-bold text-sm">⭐</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{data.statistics.high_score_products}</div>
          <div className="text-sm text-gray-600">고득점 제품</div>
        </div>
        <div className="bg-white rounded-xl p-6 border border-gray-200 text-center">
          <Lightbulb className="w-8 h-8 text-purple-500 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">{data.statistics.content_ideas_count}</div>
          <div className="text-sm text-gray-600">콘텐츠 아이디어</div>
        </div>
      </div>

      {/* Product Recommendations */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <ShoppingBag className="w-6 h-6 mr-2 text-blue-600" />
          제품 추천
        </h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {data.product_recommendations.map((product, index) => (
            <div key={index} className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{product.product}</h3>
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">{product.category}</span>
                      <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm font-medium">{product.price}</span>
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(product.trending_score)}`}>
                    {product.trending_score}점
                  </div>
                </div>
                
                <p className="text-gray-600 text-sm mb-4">{product.reason}</p>
                
                <div className="space-y-3">
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-1">구매처:</div>
                    <div className="flex flex-wrap gap-2">
                      {product.where_to_buy.map((store) => (
                        <span key={store} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">{store}</span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-1">콘텐츠 앵글:</div>
                    <div className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                      <p className="text-sm text-gray-700 flex-1">{product.content_angle}</p>
                      <button
                        onClick={() => copyToClipboard(product.content_angle, product.product)}
                        className="ml-2 p-1 text-gray-500 hover:text-gray-700 transition-colors"
                        title="복사하기"
                      >
                        {copiedProduct === product.product ? (
                          <Check className="w-4 h-4 text-green-500" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Content Ideas */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <Lightbulb className="w-6 h-6 mr-2 text-purple-600" />
          콘텐츠 아이디어
        </h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {data.content_ideas.map((idea, index) => (
            <div key={index} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex-1">{idea.title}</h3>
                <div className="flex items-center space-x-2 ml-4">
                  <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-sm">{idea.type}</span>
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">{idea.platform}</span>
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-1">훅(Hook):</div>
                  <p className="text-sm text-gray-600 bg-yellow-50 p-3 rounded-lg italic">"{idea.hook}"</p>
                </div>
                
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-2">핵심 포인트:</div>
                  <ul className="space-y-1">
                    {idea.key_points.map((point, pointIndex) => (
                      <li key={pointIndex} className="text-sm text-gray-600 flex items-start">
                        <span className="text-purple-500 mr-2">•</span>
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-1">CTA (Call to Action):</div>
                  <div className="flex items-center justify-between bg-purple-50 p-3 rounded-lg">
                    <p className="text-sm text-purple-700 flex-1">"{idea.call_to_action}"</p>
                    <button
                      onClick={() => copyToClipboard(idea.call_to_action, `idea-${index}`)}
                      className="ml-2 p-1 text-purple-500 hover:text-purple-700 transition-colors"
                      title="복사하기"
                    >
                      {copiedProduct === `idea-${index}` ? (
                        <Check className="w-4 h-4 text-green-500" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="text-center py-8 border-t border-gray-200">
        <p className="text-gray-500 text-sm">
          ✨ 이 추천은 AI가 당신의 프로필을 분석하여 개인화된 결과를 생성했습니다.
        </p>
        <p className="text-gray-400 text-xs mt-1">
          생성 시간: {formatDate(data.generated_at)}
        </p>
      </div>
    </div>
  )
} 