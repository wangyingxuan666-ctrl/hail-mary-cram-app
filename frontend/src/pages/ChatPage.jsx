import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Send, Loader2, Plus } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { startSession, getChatHistory, streamAskQuestion, getSessions } from '../services/api'

export default function ChatPage() {
  const { sessionId } = useParams()
  const [sessions, setSessions] = useState([])
  const [currentId, setCurrentId] = useState(sessionId || '')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [streamText, setStreamText] = useState('')
  const [error, setError] = useState('')
  const messagesEnd = useRef(null)

  // Load sessions
  useEffect(() => {
    getSessions().then(setSessions).catch(() => {})
  }, [currentId])

  // Load history when session changes
  useEffect(() => {
    if (currentId) {
      getChatHistory(currentId)
        .then(data => setMessages(data.messages || []))
        .catch(() => setMessages([]))
    } else {
      setMessages([])
    }
  }, [currentId])

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamText])

  const handleNewSession = async () => {
    try {
      const s = await startSession()
      setCurrentId(s.id)
      setMessages([])
    } catch (e) {
      setError(e.message)
    }
  }

  const handleSend = () => {
    if (!input.trim() || streaming || !currentId) return
    const userMsg = { id: Date.now().toString(), role: 'user', content: input, timestamp: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setStreaming(true)
    setStreamText('')
    setError('')

    streamAskQuestion(
      currentId,
      input,
      null,
      (chunk) => setStreamText(prev => prev + chunk),
      () => {
        setStreamText(prev => {
          if (prev) {
            setMessages(msgs => [...msgs, {
              id: (Date.now() + 1).toString(),
              role: 'assistant',
              content: prev,
              timestamp: new Date().toISOString(),
            }])
          }
          return ''
        })
        setStreaming(false)
      },
      (err) => {
        setError(err.message)
        setStreaming(false)
      },
    )
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="h-full flex">
      {/* Session sidebar */}
      <div className="hidden lg:flex flex-col w-56 border-r border-slate-200 bg-white">
        <div className="p-3">
          <button
            onClick={handleNewSession}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition-colors"
          >
            <Plus size={16} /> 新会话
          </button>
        </div>
        <div className="flex-1 overflow-auto">
          {sessions.map(s => (
            <button
              key={s.id}
              onClick={() => setCurrentId(s.id)}
              className={`w-full text-left px-3 py-2 text-sm transition-colors ${
                s.id === currentId ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <div className="truncate">{s.exam_paper || '未命名会话'}</div>
              <div className="text-xs text-slate-400">{s.message_count} 条消息</div>
            </button>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile session bar */}
        <div className="lg:hidden p-3 border-b bg-white flex gap-2">
          <button onClick={handleNewSession} className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-sm"><Plus size={16} /></button>
          <select
            value={currentId}
            onChange={(e) => setCurrentId(e.target.value)}
            className="flex-1 text-sm border rounded-lg px-2"
          >
            <option value="">选择会话</option>
            {sessions.map(s => (
              <option key={s.id} value={s.id}>{s.exam_paper || s.id}</option>
            ))}
          </select>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-auto p-4 space-y-4">
          {!currentId && (
            <div className="text-center py-12">
              <div className="text-4xl mb-4">💬</div>
              <h3 className="text-lg font-medium text-slate-700 mb-2">开始逐题讲解</h3>
              <p className="text-slate-500 mb-4">创建新会话或选择已有会话</p>
              <button onClick={handleNewSession} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                创建新会话
              </button>
            </div>
          )}

          {messages.map(msg => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-xl px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white border border-slate-200 text-slate-700'
              }`}>
                {msg.role === 'assistant' ? (
                  <div className="markdown-content text-sm">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                )}
              </div>
            </div>
          ))}

          {/* Streaming message */}
          {streaming && streamText && (
            <div className="flex justify-start">
              <div className="max-w-[85%] bg-white border border-indigo-200 rounded-xl px-4 py-3">
                <div className="markdown-content text-sm">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {streamText}
                  </ReactMarkdown>
                </div>
                <span className="inline-block w-2 h-4 bg-indigo-500 animate-pulse rounded-sm ml-1" />
              </div>
            </div>
          )}

          {streaming && !streamText && (
            <div className="flex justify-start">
              <div className="bg-white border border-slate-200 rounded-xl px-4 py-3">
                <Loader2 size={20} className="animate-spin text-indigo-500" />
              </div>
            </div>
          )}

          <div ref={messagesEnd} />
        </div>

        {/* Error display */}
        {error && (
          <div className="mx-4 p-2 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
        )}

        {/* Input */}
        {currentId && (
          <div className="p-4 bg-white border-t border-slate-200">
            <div className="flex gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="输入考点或题目，如：讲解 Q1(a) Deming 14点..."
                className="flex-1 px-4 py-3 border border-slate-300 rounded-xl resize-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm"
                rows={2}
                disabled={streaming}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || streaming}
                className="self-end px-4 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                {streaming ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
