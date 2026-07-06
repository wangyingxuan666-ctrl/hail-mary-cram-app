import { useState, useCallback, useEffect } from 'react'
import { Upload, FileText, Trash2, Loader2 } from 'lucide-react'
import { uploadFile, getDocuments, deleteDocument } from '../services/api'

export default function UploadPage() {
  const [docs, setDocs] = useState([])
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [error, setError] = useState('')

  const loadDocs = useCallback(async () => {
    try {
      const res = await getDocuments()
      setDocs(res.documents)
    } catch (e) {
      setError(e.message)
    }
  }, [])

  useEffect(() => { loadDocs() }, [loadDocs])

  const handleUpload = async (files, type) => {
    setUploading(true)
    setError('')
    try {
      for (const file of files) {
        await uploadFile(file, type)
      }
      await loadDocs()
    } catch (e) {
      setError(e.message)
    }
    setUploading(false)
  }

  const handleDelete = async (id) => {
    try {
      await deleteDocument(id)
      await loadDocs()
    } catch (e) {
      setError(e.message)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
  }

  const materials = docs.filter(d => d.doc_type === 'material')
  const exams = docs.filter(d => d.doc_type === 'exam')

  return (
    <div className="p-6 lg:p-8 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-800 mb-2">📤 上传资料</h1>
      <p className="text-slate-500 mb-8">上传课件（课件做索引）和历年真题（真题做主线）</p>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Materials upload */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="font-semibold text-slate-800 mb-4">📚 课件 / 课程资料</h2>
          <DropZone
            accept=".pdf,.docx,.txt"
            onFiles={(files) => handleUpload(files, 'materials')}
            uploading={uploading}
          />
          {materials.length > 0 && (
            <div className="mt-4 space-y-2">
              {materials.map(d => (
                <DocRow key={d.id} doc={d} onDelete={() => handleDelete(d.id)} />
              ))}
            </div>
          )}
        </div>

        {/* Exams upload */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="font-semibold text-slate-800 mb-4">📝 真题 / 试卷</h2>
          <DropZone
            accept=".pdf,.docx,.txt"
            onFiles={(files) => handleUpload(files, 'exams')}
            uploading={uploading}
          />
          {exams.length > 0 && (
            <div className="mt-4 space-y-2">
              {exams.map(d => (
                <DocRow key={d.id} doc={d} onDelete={() => handleDelete(d.id)} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function DropZone({ accept, onFiles, uploading }) {
  const [dragOver, setDragOver] = useState(false)

  return (
    <label
      className={`
        flex flex-col items-center justify-center gap-2 p-8 border-2 border-dashed rounded-xl cursor-pointer transition-colors
        ${dragOver ? 'border-indigo-400 bg-indigo-50' : 'border-slate-300 hover:border-slate-400'}
        ${uploading ? 'opacity-50 pointer-events-none' : ''}
      `}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => { e.preventDefault(); setDragOver(false); onFiles(e.dataTransfer.files) }}
    >
      {uploading ? (
        <>
          <Loader2 size={32} className="text-indigo-500 animate-spin" />
          <span className="text-sm text-slate-500">上传中...</span>
        </>
      ) : (
        <>
          <Upload size={32} className="text-slate-400" />
          <span className="text-sm text-slate-500">拖拽文件到此处或点击上传</span>
          <span className="text-xs text-slate-400">{accept.replace(/\./g, '').replace(/,/g, ' / ')}</span>
        </>
      )}
      <input
        type="file"
        className="hidden"
        accept={accept}
        multiple
        onChange={(e) => e.target.files && onFiles(e.target.files)}
        disabled={uploading}
      />
    </label>
  )
}

function DocRow({ doc, onDelete }) {
  return (
    <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
      <div className="flex items-center gap-3 min-w-0">
        <FileText size={16} className="text-slate-400 shrink-0" />
        <div className="min-w-0">
          <div className="text-sm text-slate-700 truncate">{doc.filename}</div>
          <div className="text-xs text-slate-400">{doc.page_count} 页 · {doc.chunk_count} 块</div>
        </div>
      </div>
      <button onClick={onDelete} className="p-1 text-slate-400 hover:text-red-500 transition-colors shrink-0">
        <Trash2 size={16} />
      </button>
    </div>
  )
}
