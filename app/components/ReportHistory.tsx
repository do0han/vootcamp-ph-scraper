'use client'

import { useState, useEffect } from 'react'
import { Clock, Download, Eye, Trash2 } from 'lucide-react'

export interface SavedReport {
  id: string
  persona_name: string
  persona_emoji: string
  title: string
  generated_at: string
  content: string
}

interface ReportHistoryProps {
  onLoadReport: (report: string) => void
}

export function ReportHistory({ onLoadReport }: ReportHistoryProps) {
  const [savedReports, setSavedReports] = useState<SavedReport[]>([])
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    loadSavedReports()
  }, [])

  const loadSavedReports = () => {
    const saved = localStorage.getItem('vootcamp_saved_reports')
    if (saved) {
      try {
        const reports = JSON.parse(saved)
        setSavedReports(reports.sort((a: SavedReport, b: SavedReport) => 
          new Date(b.generated_at).getTime() - new Date(a.generated_at).getTime()
        ))
      } catch (error) {
        console.error('Failed to parse saved reports:', error)
        setSavedReports([])
      }
    }
  }

  const saveReport = (persona_name: string, persona_emoji: string, content: string) => {
    const newReport: SavedReport = {
      id: Date.now().toString(),
      persona_name,
      persona_emoji,
      title: `${persona_name} 리포트`,
      generated_at: new Date().toISOString(),
      content
    }

    const updatedReports = [newReport, ...savedReports].slice(0, 10) // Keep only last 10 reports
    setSavedReports(updatedReports)
    localStorage.setItem('vootcamp_saved_reports', JSON.stringify(updatedReports))
  }

  const deleteReport = (id: string) => {
    const updatedReports = savedReports.filter(report => report.id !== id)
    setSavedReports(updatedReports)
    localStorage.setItem('vootcamp_saved_reports', JSON.stringify(updatedReports))
  }

  const downloadReport = (report: SavedReport) => {
    const blob = new Blob([report.content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `vootcamp-${report.persona_name}-${new Date(report.generated_at).toISOString().split('T')[0]}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Expose saveReport function to parent component
  useEffect(() => {
    // @ts-ignore - Add to window for access from parent
    window.saveReport = saveReport
  }, [savedReports])

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <Clock className="w-4 h-4" />
        <span>히스토리 ({savedReports.length})</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-96 overflow-y-auto">
          <div className="p-3 border-b border-gray-100">
            <h3 className="font-medium text-gray-900">저장된 리포트</h3>
          </div>

          {savedReports.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              저장된 리포트가 없습니다.
            </div>
          ) : (
            <div className="p-2">
              {savedReports.map((report) => (
                <div key={report.id} className="p-3 hover:bg-gray-50 rounded-lg group">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-lg">{report.persona_emoji}</span>
                        <span className="text-sm font-medium text-gray-900 truncate">
                          {report.title}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500">
                        {formatDate(report.generated_at)}
                      </p>
                    </div>

                    <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => {
                          onLoadReport(report.content)
                          setIsOpen(false)
                        }}
                        className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                        title="리포트 보기"
                      >
                        <Eye className="w-3 h-3" />
                      </button>
                      <button
                        onClick={() => downloadReport(report)}
                        className="p-1 text-gray-400 hover:text-green-600 transition-colors"
                        title="다운로드"
                      >
                        <Download className="w-3 h-3" />
                      </button>
                      <button
                        onClick={() => deleteReport(report.id)}
                        className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                        title="삭제"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}