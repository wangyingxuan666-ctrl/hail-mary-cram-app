# 临时抱佛脚 · Hail Mary Cram

> AI-powered exam cramming assistant — course materials as dictionary, past papers as anchor, explanations your grandma can understand.

AI 驱动的考前突击学习平台。**课件做索引，真题做主线，讲解奶奶都能听懂。**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-blue.svg)](https://react.dev/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-orange.svg)](https://www.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features | 功能

| Module | Description |
|--------|-------------|
| 📤 **Document Upload** | Drag-and-drop upload for course materials and past exam papers (PDF/DOCX/TXT) |
| 📊 **Frequency Analysis** | AI scans all past papers → generates topic frequency table with priority tiers (🔴必考 🟠高频 🟡中频 🟢低频) |
| 💬 **AI-Powered Q&A** | 3-section + 6-step explanation method with real-time SSE streaming |
| 🧠 **Progress Tracking** | Track mastered vs. confused topics across study sessions |
| 📄 **Document Export** | Export single-exam walkthrough, cross-year cheat sheet, or gap prediction in Markdown |

## Architecture | 架构

```
Frontend (React + Vite + Tailwind)
        ↕ REST + SSE Streaming
Backend (FastAPI + LangChain)
        ↕ OpenAI-compatible API
DeepSeek Chat API
```

### Tech Stack | 技术栈

| Layer | Technology |
|-------|-----------|
| **Backend** | Python · FastAPI · LangChain · FAISS · pdfplumber |
| **LLM** | DeepSeek Chat API |
| **Vector Store** | FAISS (in-memory semantic search) |
| **Frontend** | React 19 · TypeScript · Vite · Tailwind CSS v4 |
| **Streaming** | Server-Sent Events (SSE) |
| **Document Processing** | PyPDF · pdfplumber · python-docx |

## Quick Start | 快速开始

### Prerequisites

- Python 3.12+
- Node.js 18+
- DeepSeek API Key ([get one here](https://platform.deepseek.com/))

### Backend

```bash
cd backend
pip install -r requirements.txt

# Create .env file with your API key:
echo DEEPSEEK_API_KEY=your-key-here > .env

python -m uvicorn main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

## The 6-Step Explanation Method | 6 步讲解法

Each concept is explained following this structure:

1. **One-sentence plain language** — what it is, no textbook definitions
2. **Background story** — why it was proposed, what real problem it solved
3. **Life analogy** — at least one analogy your grandma would get
4. **Cross-application** — where else this concept applies
5. **Key exam focus** — what the question is *really* testing
6. **Common mistake warning** — the one thing students most often get wrong

## Project Structure | 项目结构

```
hail-mary-app/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Settings & environment
│   ├── models/              # Pydantic data models
│   ├── services/            # Core business logic (7 services)
│   ├── routes/              # API routers (5 groups, 20+ endpoints)
│   └── prompts/             # LLM prompt templates
├── frontend/
│   └── src/
│       ├── pages/           # 5 page components
│       ├── components/      # Reusable UI components
│       ├── services/        # API client with SSE streaming
│       └── types/           # TypeScript type definitions
└── README.md
```

## Inspired By | 灵感来源

This project is inspired by the open-source [Hail Mary Cram](https://github.com/victorzhang016-code/hail-mary) Claude Code plugin by [@Victor Zhang](https://github.com/victorzhang016-code) — evolved from a CLI skill into a full-stack web application.

## License

MIT
