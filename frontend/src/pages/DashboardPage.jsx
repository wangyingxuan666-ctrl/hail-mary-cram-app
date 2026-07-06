import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, FileText, BarChart3, MessageSquare, TrendingUp } from 'lucide-react'
import { getDocuments, getFrequency, getMemorySummary, getSessions } from '../services/api'

export default function DashboardPage() {
  const [stats, setStats] = useState({ docs: 0, topics: 0, sessions: 0, mastered: 0, total: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [docsRes, freqRes, memRes, sessionsRes] = await Promise.allSettled([
          getDocuments(),
          getFrequency(),
          getMemorySummary(),
          getSessions(),
        ])
        setStats({
          docs: docsRes.status === 'fulfilled' ? docsRes.value.total : 0,
          topics: freqRes.status === 'fulfilled' ? freqRes.value.topics?.length || 0 : 0,
          sessions: sessionsRes.status === 'fulfilled' ? sessionsRes.value.length || 0 : 0,
          mastered: memRes.status === 'fulfilled' ? memRes.value.mastered || 0 : 0,
          total: memRes.status === 'fulfilled' ? memRes.value.total || 0 : 0,
        })
      } catch {}
      setLoading(false)
    }
    load()
  }, [])

  const cards = [
    { label: '已上传文件', value: stats.docs, icon: FileText, color: 'bg-blue-500', to: '/upload' },
    { label: '已识别考点', value: stats.topics, icon: BarChart3, color: 'bg-orange-500', to: '/analysis' },
    { label: '学习会话', value: stats.sessions, icon: MessageSquare, color: 'bg-green-500', to: '/chat' },
    { label: '已掌握考点', value: `${stats.mastered}/${stats.total}`, icon: TrendingUp, color: 'bg-purple-500', to: '/analysis' },
  ]

  return (
    <div className="p-6 lg:p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-800">📚 临时抱佛脚</h1>
        <p className="text-slate-500 mt-1">真题驱动的考前突击 AI 助教 — 课件做索引，真题做主线，奶奶都能听懂</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {cards.map(({ label, value, icon: Icon, color, to }) => (
          <Link key={label} to={to} className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3 mb-3">
              <div className={`w-10 h-10 ${color} rounded-lg flex items-center justify-center`}>
                <Icon size={20} className="text-white" />
              </div>
              <span className="text-sm text-slate-500">{label}</span>
            </div>
            <div className="text-2xl font-bold text-slate-800">
              {loading ? <div className="h-8 w-16 bg-slate-100 rounded animate-pulse" /> : value}
            </div>
          </Link>
        ))}
      </div>

      {/* Quick actions */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">🚀 快速开始</h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <Link to="/upload" className="flex items-center gap-3 p-4 rounded-lg border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50 transition-colors">
            <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center text-2xl">📤</div>
            <div>
              <div className="font-medium text-slate-800">上传资料</div>
              <div className="text-sm text-slate-500">上传课件 + 历年真题</div>
            </div>
          </Link>
          <Link to="/analysis" className="flex items-center gap-3 p-4 rounded-lg border border-slate-200 hover:border-orange-300 hover:bg-orange-50/50 transition-colors">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center text-2xl">📊</div>
            <div>
              <div className="font-medium text-slate-800">考点分析</div>
              <div className="text-sm text-slate-500">AI 扫描真题生成频率表</div>
            </div>
          </Link>
          <Link to="/chat" className="flex items-center gap-3 p-4 rounded-lg border border-slate-200 hover:border-green-300 hover:bg-green-50/50 transition-colors">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-2xl">💬</div>
            <div>
              <div className="font-medium text-slate-800">开始讲解</div>
              <div className="text-sm text-slate-500">逐题对话式讲解，奶奶都能懂</div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  )
}
