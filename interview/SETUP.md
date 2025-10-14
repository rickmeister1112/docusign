# Quick Setup Guide

## Prerequisites
- Node.js (v18+)
- Python (v3.8+)
- npm

## Quick Start

### 1. Start the Backend Server
```bash
# Terminal 1
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend Server
```bash
# Terminal 2
cd frontend
npm run dev
```

### 3. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Alternative: Use the Startup Scripts
```bash
# Terminal 1
./start-backend.sh

# Terminal 2
./start-frontend.sh
```

## Features
- ✅ Submit feedback via form
- ✅ View all feedback entries
- ✅ Delete feedback with confirmation
- ✅ Responsive design
- ✅ Real-time updates
- ✅ Error handling
- ✅ TypeScript support
- ✅ SQLite database
- ✅ FastAPI with auto-docs

## Project Structure
```
interview/
├── frontend/          # React + Vite app
├── backend/           # FastAPI app
├── start-backend.sh   # Backend startup script
├── start-frontend.sh  # Frontend startup script
└── README.md         # Full documentation
``` 