import { useState } from 'react'
import { FileText, Download, Loader2, FileDown, BookOpen } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  exportSingleExam, exportCrossYear, exportGapPrediction,
  listExports, getDownloadUrl,
} from '../services/api'

export default function ExportPage() {
  const [loading, setLoading] = useState('')
  const [preview, setPreview] = useState(null)
  const [filename, setFilename] = useState('')
  const [error, setError] = useState('')
  const [examYear, setExamYear] = useState('')
  const [predYear, setPredYear] = useState('')

  const handleExport = async (type) => {
    setLoading(type)
    setError('')
    setPreview(null)
    try {
      let result
      if (type === 'single') result = await exportSingleExam(examYear)
      else if (type === 'cross') result = await exportCrossYear()
      else if (type === 'gap') result = await exportGapPrediction(predYear)
      setPreview(result.content)
      setFilename(result.filename)
    } catch (e) {
      setError(e.message)
    }
    setLoading('')
  }

  const exports = [
    {
      type: 'single',
      title: '单卷真题讲解',
      icon: FileText,
      desc: '逐题讲解 + 考点归类 + 失分提醒',
      color: 'border-blue-200 hover:border-blue-400 bg-blue-50/30',
      yearInput: true,
    },
    {
      type: 'cross',
      title: '跨卷对照速记卡',
      icon: BookOpen,
      desc: '多年共用考点 + 考场 5 分钟可默写',
      color: 'border-green-200 hover:border-green-400 bg-green-50/30',
    },
    {
      type: 'gap',
      title: '补漏预测',
      icon: FileDown,
      desc: '低频/未考考点预测 + 1 页 A4 极简版',
      color: 'border-orange-200 hover:border-orange-400 bg-orange-50/30',
      yearInput: true,
    },
  ]

  return (
    <div className="p-6 lg:p-8 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-800 mb-2">📄 导出文档</h1>
      <p className="text-slate-500 mb-8">将讲解内容导出为 Markdown 文档，可在本地查看和编辑</p>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
        {exports.map(({ type, title, icon: Icon, desc, color, yearInput }) => (
          <div key={type} className={`bg-white rounded-xl border-2 p-6 ${color} transition-colors`}>
            <div className="flex items-center gap-3 mb-3">
              <Icon size={24} className="text-slate-600" />
              <h3 className="font-semibold text-slate-800">{title}</h3>
            </div>
            <p className="text-sm text-slate-500 mb-4">{desc}</p>

            {yearInput && (
              <input
                type="text"
                placeholder="年份（如 2024）"
                value={type === 'single' ? examYear : predYear}
                onChange={(e) => type === 'single' ? setExamYear(e.target.value) : setPredYear(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm mb-3 focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            )}

            <button
              onClick={() => handleExport(type)}
              disabled={loading === type}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 disabled:opacity-50 transition-colors text-sm"
            >
              {loading === type ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
              生成文档
            </button>
          </div>
        ))}
      </div>

      {/* Preview */}
      {preview && (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="font-semibold text-slate-800">📝 预览：{filename}</h2>
            <a
              href={getDownloadUrl(filename)}
              download={filename}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
            >
              <Download size={16} /> 下载
            </a>
          </div>
          <div className="p-6 markdown-content max-h-[600px] overflow-auto">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {preview}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}
