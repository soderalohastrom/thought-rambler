# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend (thought-ramble-parser/)
```bash
# Development
cd thought-ramble-parser
pnpm install
pnpm dev          # Start dev server at http://localhost:5173

# Building & Production
pnpm build        # TypeScript compile + Vite build  
pnpm build:prod   # Production build with BUILD_MODE=prod
pnpm preview      # Preview production build
pnpm vercel-build # Vercel-specific build command

# Code Quality
pnpm lint         # ESLint checking
```

### Backend (backend/)
```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Development
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Testing
python test_api.py
```

### Deployment
```bash
# Vercel deployment (recommended)
vercel --prod

# Local Docker (alternative)
# Backend: docker build -t thought-parser-backend . && docker run -p 8000:8000 --env-file .env thought-parser-backend
# Frontend: pnpm build && pnpm preview
```

## Architecture Overview

### Full-Stack Monorepo Structure
- **Frontend**: React 18 + TypeScript + Vite 6 in `thought-ramble-parser/`
- **Backend**: FastAPI + Python 3.11+ in `backend/`
- **Deployment**: Unified Vercel deployment via `vercel.json`

### Frontend Architecture (thought-ramble-parser/)
- **UI Framework**: React with dual-panel layout (InputPanel + OutputPanel)
- **Styling**: Tailwind CSS + Radix UI primitives for consistent design system
- **Component Structure**:
  - `src/components/InputPanel.tsx` - Text input and sample data loading
  - `src/components/OutputPanel.tsx` - Parsed thought results display
  - `src/components/ui/` - Radix-based UI components (button, card, textarea, etc.)
- **State Management**: React hooks for API communication and loading states
- **API Integration**: Centralized in `src/lib/api.ts` with TypeScript interfaces

### Backend Architecture (backend/)
- **Framework**: FastAPI with async support and automatic OpenAPI docs
- **NLP Processing**: Rule-based thought parsing using `SimpleThoughtParser` class
- **Key Features**:
  - Linguistic boundary detection using transition markers
  - Sentiment analysis and keyword extraction
  - Confidence scoring for parsed chunks
- **API Endpoints**:
  - `GET /health` - System health check
  - `POST /api/parse-thoughts` - Main thought parsing endpoint

### Thought Parsing Algorithm
The `SimpleThoughtParser` class implements:
1. **Text Preprocessing**: Normalize whitespace, filter speech patterns (um, uh)
2. **Sentence Segmentation**: Split on punctuation + conjunctions (and, but, so, then)
3. **Boundary Detection**: Identify thought transitions using transition markers:
   - Temporal: then, next, meanwhile, now
   - Logical: but, however, although
   - Topic shift: speaking of, by the way, oh
   - Decision: I should, I need to, let me
4. **Enhancement**: Add keyword extraction + basic sentiment analysis
5. **Confidence Scoring**: Provide reliability metrics for each chunk

### Key Data Models (TypeScript/Python)
```typescript
interface ThoughtChunk {
  id: number;
  text: string;
  confidence: number;
  start_char: number;
  end_char: number;
  topic_keywords: string[];
  sentiment: "positive" | "negative" | "neutral";
}

interface ThoughtParseResponse {
  chunks: ThoughtChunk[];
  total_chunks: number;
  processing_time: number;
  metadata: {
    input_length: number;
    provider: string;
    model: string;
    average_chunk_length: number;
  };
}
```

## Deployment Configuration

### Vercel Setup
- **Build Process**: Builds both frontend (static) and backend (serverless function)
- **Frontend**: Static build deployed from `thought-ramble-parser/dist/`
- **Backend**: Python serverless function with 30s timeout, 50MB max size
- **Routing**: API routes (`/api/*`, `/health`) → backend, all others → frontend

### Environment Variables
Required for LLM providers (optional for basic functionality):
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

## Development Notes

### Frontend Package Structure
Uses extensive Radix UI component library with custom styling:
- All scripts include `yes | pnpm install` for automatic dependency resolution
- Vite temp cleanup in build scripts: `rm -rf node_modules/.vite-temp`
- TypeScript strict mode with separate configs for app and build tools

### Backend Dependencies
- **Core**: FastAPI, Uvicorn, spaCy, Pydantic
- **LLM Support**: OpenAI SDK, Anthropic SDK (for future LLM integration)
- **NLP**: Currently rule-based, prepared for spaCy-LLM integration

### Local Development Workflow
1. Start backend: `cd backend && uvicorn app:app --reload --host 0.0.0.0 --port 8000`
2. Start frontend: `cd thought-ramble-parser && pnpm dev`
3. Access app at http://localhost:5173, API docs at http://localhost:8000/docs
4. Test with sample data buttons (Small ~200w, Medium ~500w, Large ~800w)

### CORS Configuration
Backend allows all origins (`allow_origins=["*"]`) - configure for production security.

### File Organization
- Frontend source in `thought-ramble-parser/src/`
- Backend logic concentrated in single `backend/app.py` file
- Sample data in `backend/sample_data.py` and `thought-ramble-parser/public/data/`
- Deployment config in root-level `vercel.json`