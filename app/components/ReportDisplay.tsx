'use client'

import { useState } from 'react'
import { Copy, Check } from 'lucide-react'

interface ReportDisplayProps {
  report: string
}

export function ReportDisplay({ report }: ReportDisplayProps) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = () => {
    navigator.clipboard.writeText(report)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Simple markdown-to-HTML converter for basic formatting
  const formatReport = (text: string) => {
    return text
      .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold text-gray-900 mb-4">$1</h1>')
      .replace(/^## (.*$)/gm, '<h2 class="text-xl font-semibold text-gray-800 mb-3 mt-6">$1</h2>')
      .replace(/^### (.*$)/gm, '<h3 class="text-lg font-medium text-gray-700 mb-2 mt-4">$1</h3>')
      .replace(/^\* (.*$)/gm, '<li class="text-gray-600 mb-1">$1</li>')
      .replace(/^- (.*$)/gm, '<li class="text-gray-600 mb-1">$1</li>')
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      .replace(/^(?!<[hl]|<li)(.*$)/gm, '<p class="text-gray-600 mb-2">$1</p>')
      .replace(/(<li.*<\/li>)/gm, '<ul class="list-disc list-inside space-y-1 mb-4">$1</ul>')
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">생성된 리포트</h3>
          <button
            onClick={copyToClipboard}
            className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 mr-1.5 text-green-500" />
                복사됨
              </>
            ) : (
              <>
                <Copy className="w-4 h-4 mr-1.5" />
                복사
              </>
            )}
          </button>
        </div>
        
        <div 
          className="prose prose-sm max-w-none"
          dangerouslySetInnerHTML={{ __html: formatReport(report) }}
        />
      </div>
    </div>
  )
} 