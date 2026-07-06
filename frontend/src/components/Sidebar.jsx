import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Upload, BarChart3, MessageSquare, FileText, X, BookOpen
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard', zh: '总览' },
  { to: '/upload', icon: Upload, label: 'Upload', zh: '上传资料' },
  { to: '/analysis', icon: BarChart3, label: 'Analysis', zh: '考点分析' },
  { to: '/chat', icon: MessageSquare, label: 'Study Q&A', zh: '逐题讲解' },
  { to: '/export', icon: FileText, label: 'Export', zh: '导出文档' },
]

export default function Sidebar({ onClose }) {
  return (
    <div className="h-full bg-white border-r border-slate-200 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center">
              <BookOpen size={20} className="text-white" />
            </div>
            <div>
              <h1 className="font-bold text-slate-800 leading-tight">临时抱佛脚</h1>
              <p className="text-xs text-slate-400">Hail Mary Cram</p>
            </div>
          </div>
          <button onClick={onClose} className="lg:hidden p-1 rounded hover:bg-slate-100">
            <X size={20} />
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label, zh }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            onClick={onClose}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`
            }
          >
            <Icon size={18} />
            <span>{zh}</span>
            <span className="text-xs text-slate-400 ml-auto hidden lg:block">{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-100">
        <p className="text-xs text-slate-400 text-center">
          真题驱动 · 奶奶都能听懂
        </p>
      </div>
    </div>
  )
}
