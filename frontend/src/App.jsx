import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import DashboardPage from './pages/DashboardPage'
import UploadPage from './pages/UploadPage'
import AnalysisPage from './pages/AnalysisPage'
import ChatPage from './pages/ChatPage'
import ExportPage from './pages/ExportPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/analysis" element={<AnalysisPage />} />
        <Route path="/chat/:sessionId?" element={<ChatPage />} />
        <Route path="/export" element={<ExportPage />} />
      </Routes>
    </Layout>
  )
}

export default App
