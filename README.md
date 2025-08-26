# Thought Ramble Parser

A React-Vite application for splitting human thought rambles using spaCy LLM integration. This tool parses stream-of-consciousness text (like STT from walkie-talkie conversations) into coherent thought chunks.

## Features

- **Clean Dual-Panel Interface**: Input on the left, parsed results on the right
- **Sample Data Testing**: Three test buttons (Small, Medium, Large) with realistic thought rambles
- **Advanced NLP Processing**: Backend API with spaCy-llm integration for thought parsing
- **Visual Chunking Display**: Color-coded parsed thought groups with sentiment analysis
- **Configurable LLM Support**: Environment variable support for OpenAI, Anthropic, and other providers
- **Professional Design**: Modern, responsive interface with subtle animations
- **Real-time Processing**: Fast thought parsing with visual feedback

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite 6** for fast development and optimized builds
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Custom UI Components** built with Radix primitives

### Backend
- **FastAPI** for high-performance API
- **spaCy** with LLM integration for advanced NLP
- **Python 3.11+** with modern async support
- **CORS enabled** for frontend integration

## Quick Start

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.11+
- API keys for LLM providers (optional for basic functionality)

### Development Setup

1. **Clone and setup backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (optional)
   ```

3. **Start backend server:**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Setup and start frontend:**
   ```bash
   cd ../thought-ramble-parser
   pnpm install
   pnpm dev
   ```

5. **Open application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Usage

1. **Load Sample Data**: Click on Small, Medium, or Large buttons to load realistic thought rambles
2. **Enter Text**: Type or paste your stream-of-consciousness text in the left panel
3. **Parse Thoughts**: Click "Parse Thoughts" to analyze the text
4. **View Results**: See color-coded thought chunks with keywords and sentiment analysis

### Sample Thought Types

- **Small (~100-200 words)**: Basic thoughts and tasks
- **Medium (~300-500 words)**: Multiple topic shifts and planning
- **Large (~800+ words)**: Complex rambling sessions with multiple themes

## API Reference

### Core Endpoints

- `GET /health` - Health check and system status
- `POST /api/parse-thoughts` - Main thought parsing endpoint

### Request Format
```json
{
  "text": "Your rambling text here...",
  "provider": "openai",
  "model": "gpt-3.5-turbo"
}
```

### Response Format
```json
{
  "chunks": [
    {
      "id": 1,
      "text": "Parsed thought chunk...",
      "confidence": 0.85,
      "topic_keywords": ["keyword1", "keyword2"],
      "sentiment": "neutral"
    }
  ],
  "total_chunks": 3,
  "processing_time": 0.125,
  "metadata": {
    "input_length": 256,
    "average_chunk_length": 85
  }
}
```

## Deployment

### Vercel (Recommended)

1. **Configure environment variables in Vercel dashboard:**
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`

2. **Deploy:**
   ```bash
   vercel --prod
   ```

### Docker Alternative

1. **Build and run backend:**
   ```bash
   cd backend
   docker build -t thought-parser-backend .
   docker run -p 8000:8000 --env-file .env thought-parser-backend
   ```

2. **Build and serve frontend:**
   ```bash
   cd thought-ramble-parser
   pnpm build
   pnpm preview
   ```

### Environment Variables

```bash
# LLM API Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
```

## Architecture

### Frontend Architecture
- **Component-based**: Modular React components with TypeScript
- **State Management**: React hooks and context for API state
- **Styling**: Tailwind CSS with custom design system
- **API Integration**: Centralized API service with error handling

### Backend Architecture
- **FastAPI**: High-performance async API framework
- **NLP Pipeline**: spaCy-based text processing with thought boundary detection
- **Rule-based Parsing**: Advanced linguistic analysis for thought chunking
- **Extensible Design**: Easy integration of additional LLM providers

### Thought Parsing Algorithm
1. **Text Preprocessing**: Clean and normalize input text
2. **Sentence Segmentation**: Split text using punctuation and conjunctions
3. **Boundary Detection**: Identify thought transitions using linguistic markers
4. **Enhancement**: Add keyword extraction and sentiment analysis
5. **Confidence Scoring**: Provide reliability metrics for each chunk

## Development

### Project Structure
```
├── backend/                 # Python FastAPI backend
│   ├── app.py              # Main application
│   ├── sample_data.py      # Sample ramble data
│   ├── test_api.py         # API testing script
│   └── requirements.txt    # Python dependencies
├── thought-ramble-parser/  # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── lib/           # Utilities and API
│   │   └── App.tsx        # Main application
│   └── public/data/       # Static sample data
└── docs/                  # Documentation
```

### Testing

**Backend Testing:**
```bash
cd backend
python test_api.py
```

**Frontend Testing:**
```bash
cd thought-ramble-parser
pnpm test
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit a pull request with detailed description

## License

MIT License - see LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on the repository.
