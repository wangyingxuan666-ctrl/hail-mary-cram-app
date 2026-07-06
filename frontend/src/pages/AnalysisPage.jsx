import { useState, useEffect } from 'react'
import { Loader2, RefreshCw } from 'lucide-react'
import { getFrequency, generateFrequency } from '../services/api'

export default function AnalysisPage() {
  const [freq, setFreq] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [courseName, setCourseName] = useState('')

  const loadFreq = async () => {
    try {
      const data = await getFrequency()
      if (data.topics?.length) setFreq(data)
    } catch {}
  }

  useEffect(() => { loadFreq() }, [])

  const handleGenerate = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await generateFrequency(courseName)
      setFreq(data)
    } catch (e) {
      setError(e.message)
    }
    setLoading(false)
  }

  const priorityColor = {
    '🔴': 'bg-red-100 text-red-700 border-red-200',
    '🟠': 'bg-orange-100 text-orange-700 border-orange-200',
    '🟡': 'bg-yellow-100 text-yellow-700 border-yellow-200',
    '🟢': 'bg-green-100 text-green-700 border-green-200',
  }

  const priorityLabel = {
    '🔴': '必考',
    '🟠': '高频',
    '🟡': '中频',
    '🟢': '低频',
  }

  return (
    <div className="p-6 lg:p-8 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">📊 考点频率分析</h1>
          <p className="text-slate-500 mt-1">AI 扫描历年真题，自动归纳考点出现频率</p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
          {freq ? '重新分析' : '开始分析'}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
      )}

      {/* Input for course name */}
      {!freq && !loading && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6">
          <label className="block text-sm font-medium text-slate-700 mb-2">课程名称（可选）</label>
          <input
            type="text"
            value={courseName}
            onChange={(e) => setCourseName(e.target.value)}
            placeholder="如：DASE7909 质量管理"
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
          />
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <Loader2 size={40} className="animate-spin text-indigo-500 mx-auto mb-4" />
          <p className="text-slate-500">AI 正在扫描真题，提取考点频率...</p>
          <p className="text-sm text-slate-400 mt-1">这可能需要 30-60 秒</p>
        </div>
      )}

      {/* Frequency Table */}
      {freq && freq.topics?.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="p-6 border-b border-slate-100">
            <h2 className="font-semibold text-slate-800">
              {freq.course_name || '课程'} — 共 {freq.total_exam_years} 年真题
            </h2>
            <div className="flex gap-4 mt-2">
              {Object.entries(priorityLabel).map(([emoji, label]) => (
                <span key={emoji} className={`text-xs px-2 py-0.5 rounded border ${priorityColor[emoji]}`}>
                  {emoji} {label} (≥{{ '🔴': 50, '🟠': 30, '🟡': 20, '🟢': 0 }[emoji]}%)
                </span>
              ))}
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-slate-50 text-left">
                  <th className="p-3 text-sm font-medium text-slate-600">考点</th>
                  <th className="p-3 text-sm font-medium text-slate-600">出现年份</th>
                  <th className="p-3 text-sm font-medium text-slate-600">频率</th>
                  <th className="p-3 text-sm font-medium text-slate-600">优先级</th>
                  <th className="p-3 text-sm font-medium text-slate-600">相关题目</th>
                </tr>
              </thead>
              <tbody>
                {freq.topics.map((t, i) => (
                  <tr key={i} className="border-t border-slate-100 hover:bg-slate-50/50">
                    <td className="p-3 text-sm font-medium text-slate-800">{t.topic_name}</td>
                    <td className="p-3 text-sm text-slate-600">{t.years.join(' / ')}</td>
                    <td className="p-3 text-sm text-slate-600">
                      {t.frequency_count}/{t.total_years} ({t.frequency_pct}%)
                    </td>
                    <td className="p-3">
                      <span className={`inline-block text-xs px-2 py-0.5 rounded border ${priorityColor[t.priority]}`}>
                        {t.priority} {priorityLabel[t.priority]}
                      </span>
                    </td>
                    <td className="p-3 text-xs text-slate-500">{t.related_questions?.join(', ') || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!freq && !loading && !error && (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <div className="text-4xl mb-4">📋</div>
          <h3 className="text-lg font-medium text-slate-700 mb-2">暂无考点数据</h3>
          <p className="text-slate-500 mb-4">请先上传真题文件，然后点击"开始分析"</p>
        </div>
      )}
    </div>
  )
}
