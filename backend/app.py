import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Thought Ramble Parser", description="API for parsing human thought rambles using advanced NLP")

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple NLP model initialization
parser_ready = True

def initialize_nlp_model():
    """Initialize simplified NLP processing"""
    global parser_ready
    try:
        # For now, we'll use rule-based processing instead of spaCy
        parser_ready = True
        logger.info("NLP parser initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize NLP parser: {e}")
        parser_ready = False

# Request/Response models
class ThoughtParseRequest(BaseModel):
    text: str
    provider: str = "openai"  # openai, anthropic, etc.
    model: str = "gpt-3.5-turbo"
    enable_llm: bool = False  # Enable LLM-enhanced processing

class ThoughtChunk(BaseModel):
    id: int
    text: str
    confidence: float
    start_char: int
    end_char: int
    topic_keywords: List[str]
    sentiment: str

class ThoughtParseResponse(BaseModel):
    chunks: List[ThoughtChunk]
    total_chunks: int
    processing_time: float
    metadata: Dict[str, Any]

class SimpleThoughtParser:
    """Simplified thought parsing using rule-based NLP techniques"""
    
    def __init__(self):
        self.transition_markers = {
            'temporal': ['then', 'next', 'after', 'before', 'meanwhile', 'now', 'later'],
            'logical': ['but', 'however', 'although', 'though', 'nevertheless', 'anyway'],
            'additive': ['also', 'additionally', 'furthermore', 'moreover'],
            'topic_shift': ['speaking of', 'by the way', 'oh', 'wait', 'actually', 'I mean'],
            'decision': ['I should', 'I need to', 'I have to', 'let me'],
            'memory': ['I remember', 'I forgot', 'I was thinking', 'I realized']
        }
        
    def parse_thoughts(self, text: str, provider: str = "openai", model: str = "gpt-3.5-turbo") -> List[Dict[str, Any]]:
        """Parse rambling text into coherent thought chunks using rule-based approach"""
        
        # Basic preprocessing
        text = self._preprocess_text(text)
        
        # Split into sentences using simple rule-based approach
        sentences = self._split_sentences(text)
        
        # Advanced thought chunk detection using multiple strategies
        chunks = self._detect_thought_boundaries(sentences, text)
        
        # Enhance chunks with basic analysis
        enhanced_chunks = self._enhance_with_analysis(chunks, provider, model)
        
        return enhanced_chunks
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize input text"""
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Handle common speech patterns
        text = re.sub(r'\b(um|uh|er|ah)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text)  # Clean up spaces again
        
        return text
    
    def _split_sentences(self, text: str) -> List[str]:
        """Simple sentence splitting using punctuation and conjunctions"""
        # Split on periods, exclamations, questions
        sentences = re.split(r'[.!?]+', text)
        
        # Further split on strong transition markers
        result = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Split on strong conjunctions
            parts = re.split(r'\b(and|but|so|then)\b', sentence)
            
            current_part = ""
            for i, part in enumerate(parts):
                part = part.strip()
                if not part:
                    continue
                
                if part.lower() in ['and', 'but', 'so', 'then'] and current_part:
                    result.append(current_part.strip())
                    current_part = ""
                else:
                    current_part += " " + part if current_part else part
            
            if current_part.strip():
                result.append(current_part.strip())
        
        return [s for s in result if len(s.strip()) > 10]  # Filter out very short segments
    
    def _detect_thought_boundaries(self, sentences: List[str], original_text: str) -> List[Dict[str, Any]]:
        """Detect thought boundaries using linguistic cues in sentences"""
        chunks = []
        current_chunk = []
        current_start = 0
        
        for i, sentence in enumerate(sentences):
            sentence_text = sentence.strip()
            
            # Check for transition markers
            should_split = self._should_split_here(sentence_text)
            
            # Check for topic coherence with previous sentences
            if i > 0 and should_split:
                # Finalize current chunk
                if current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    chunks.append({
                        'text': chunk_text,
                        'start_char': current_start,
                        'end_char': current_start + len(chunk_text),
                        'sentence_count': len(current_chunk)
                    })
                    
                # Start new chunk
                current_chunk = [sentence_text]
                current_start = original_text.find(sentence_text, current_start)
            else:
                current_chunk.append(sentence_text)
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'start_char': current_start,
                'end_char': current_start + len(chunk_text),
                'sentence_count': len(current_chunk)
            })
        
        return chunks
    
    def _should_split_here(self, sentence_text: str) -> bool:
        """Determine if we should split at this sentence"""
        sentence_lower = sentence_text.lower()
        
        # Check for explicit transition markers
        for category, markers in self.transition_markers.items():
            for marker in markers:
                if sentence_lower.startswith(marker) or f' {marker} ' in sentence_lower:
                    return True
        
        # Check for question-to-statement transitions
        if '?' in sentence_text:
            return True
            
        # Check for very long sentences (often contain multiple thoughts)
        if len(sentence_text.split()) > 15:
            return True
            
        return False
    
    def _enhance_with_analysis(self, chunks: List[Dict], provider: str, model: str) -> List[Dict[str, Any]]:
        """Enhance chunks with basic NLP analysis"""
        enhanced_chunks = []
        
        for i, chunk in enumerate(chunks):
            # Basic sentiment analysis using keyword matching
            sentiment = self._analyze_sentiment(chunk['text'])
            
            # Extract keywords using simple frequency analysis
            keywords = self._extract_keywords(chunk['text'])
            
            enhanced_chunk = {
                'id': i + 1,
                'text': chunk['text'],
                'confidence': 0.85,  # Placeholder confidence score
                'start_char': chunk['start_char'],
                'end_char': chunk['end_char'],
                'topic_keywords': keywords,
                'sentiment': sentiment
            }
            
            enhanced_chunks.append(enhanced_chunk)
        
        return enhanced_chunks
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis"""
        # This is a placeholder - in production, you'd use the LLM API
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'happy', 'excited']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'sad', 'angry', 'frustrated']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text using simple analysis"""
        # Common stop words to filter out
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'about', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'would', 'could', 'should'}
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = []
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and take top words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:5]]
        
        # Also look for capitalized words (likely names/places)
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', text)
        for word in capitalized:
            if word.lower() not in stop_words and word.lower() not in [k.lower() for k in keywords]:
                keywords.append(word)
        
        return keywords[:5]  # Return top 5 unique keywords

# Initialize the parser
parser = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global parser
    initialize_nlp_model()
    if parser_ready:
        parser = SimpleThoughtParser()
        logger.info("Thought parser initialized successfully")
    else:
        logger.error("Failed to initialize thought parser")

@app.get("/")
async def root():
    return {"message": "Thought Ramble Parser API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "nlp_ready": parser_ready,
        "parser_ready": parser is not None
    }

@app.post("/api/parse-thoughts", response_model=ThoughtParseResponse)
async def parse_thoughts(request: ThoughtParseRequest):
    """Main endpoint for parsing thought rambles"""
    if not parser:
        raise HTTPException(status_code=503, detail="Parser not initialized. Please ensure spaCy model is loaded.")
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty")
    
    try:
        import time
        start_time = time.time()
        
        # Parse the thoughts
        chunks = parser.parse_thoughts(request.text, request.provider, request.model)
        
        processing_time = time.time() - start_time
        
        # Convert to response format
        thought_chunks = [ThoughtChunk(**chunk) for chunk in chunks]
        
        response = ThoughtParseResponse(
            chunks=thought_chunks,
            total_chunks=len(thought_chunks),
            processing_time=processing_time,
            metadata={
                "input_length": len(request.text),
                "provider": request.provider,
                "model": request.model,
                "average_chunk_length": sum(len(chunk.text) for chunk in thought_chunks) / len(thought_chunks) if thought_chunks else 0
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error parsing thoughts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@app.post("/api/parse-thoughts-llm", response_model=ThoughtParseResponse)
async def parse_thoughts_llm(request: ThoughtParseRequest):
    """Enhanced endpoint for parsing thought rambles with LLM-based relationship detection"""
    if not parser:
        raise HTTPException(status_code=503, detail="Parser not initialized. Please ensure spaCy model is loaded.")
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty")
    
    try:
        import time
        start_time = time.time()
        
        # Check if LLM enhancement is enabled and available
        llm_available = False
        enhanced_chunks = []
        
        if request.enable_llm:
            try:
                from models.gemma_loader import get_gemma_model
                from spacy_llm_tasks.chunk_relationship import merge_related_chunks, ChunkRelationship
                
                gemma = get_gemma_model()
                if gemma.is_available():
                    llm_available = True
                    logger.info("LLM enhancement enabled - using Gemma for relationship detection")
                    enhanced_chunks = await parse_thoughts_with_llm_sync(request.text, request.provider, request.model, parser)
                else:
                    logger.warning("Gemma model not available, falling back to basic parsing")
            except ImportError as e:
                logger.warning(f"LLM components not available: {e}")
            except Exception as e:
                logger.error(f"LLM enhancement failed: {e}")
        
        # Fallback to basic parsing if LLM is disabled or failed
        if not enhanced_chunks:
            enhanced_chunks = parser.parse_thoughts(request.text, request.provider, request.model)
        
        processing_time = time.time() - start_time
        
        # Convert to response format
        thought_chunks = [ThoughtChunk(**chunk) for chunk in enhanced_chunks]
        
        response = ThoughtParseResponse(
            chunks=thought_chunks,
            total_chunks=len(thought_chunks),
            processing_time=processing_time,
            metadata={
                "input_length": len(request.text),
                "provider": request.provider,
                "model": request.model,
                "llm_enhanced": llm_available and request.enable_llm,
                "average_chunk_length": sum(len(chunk.text) for chunk in thought_chunks) / len(thought_chunks) if thought_chunks else 0
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in LLM-enhanced parsing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing text with LLM: {str(e)}")

async def parse_thoughts_with_llm_sync(text: str, provider: str, model: str, parser) -> List[Dict[str, Any]]:
    """Synchronous wrapper for LLM-enhanced parsing"""
    try:
        from models.gemma_loader import get_gemma_model
        from spacy_llm_tasks.chunk_relationship import merge_related_chunks, ChunkRelationship
        
        # Step 1: Get basic chunks
        basic_chunks = parser.parse_thoughts(text, provider, model)
        
        if len(basic_chunks) < 2:
            return basic_chunks
        
        # Step 2: Use Gemma for relationship detection
        gemma = get_gemma_model()
        relationships = []
        
        for i, chunk1 in enumerate(basic_chunks):
            for j in range(i + 1, min(i + 4, len(basic_chunks))):  # Check within 3-chunk window
                chunk2 = basic_chunks[j]
                
                # Create relationship prompt
                prompt = create_relationship_prompt(chunk1['text'], chunk2['text'])
                
                try:
                    response = gemma([prompt])[0]
                    relationship = parse_relationship_response(response, i, j)
                    
                    if relationship and relationship.confidence >= 0.7:
                        relationships.append(relationship)
                        logger.info(f"Found relationship: {i}-{j} ({relationship.relationship_type}, {relationship.confidence})")
                
                except Exception as e:
                    logger.warning(f"Failed to analyze relationship {i}-{j}: {e}")
                    continue
        
        # Step 3: Merge related chunks
        if relationships:
            enhanced_chunks = merge_related_chunks(basic_chunks, relationships)
            logger.info(f"Merged {len(basic_chunks)} -> {len(enhanced_chunks)} chunks")
            return enhanced_chunks
        else:
            return basic_chunks
            
    except Exception as e:
        logger.error(f"LLM processing failed: {e}")
        return basic_chunks

def create_relationship_prompt(chunk1_text: str, chunk2_text: str) -> str:
    """Create a prompt for relationship analysis"""
    return f"""Analyze if these two text segments are related:

Segment 1: "{chunk1_text}"
Segment 2: "{chunk2_text}"

Consider if they discuss the same topic, person, event, or are causally related.

Respond with:
RELATIONSHIP: [SAME_TOPIC|SAME_PERSON|SAME_EVENT|CAUSE_EFFECT|TEMPORAL|NONE]
CONFIDENCE: [0.0 to 1.0]

Example:
RELATIONSHIP: SAME_PERSON
CONFIDENCE: 0.95"""

def parse_relationship_response(response: str, chunk1_id: int, chunk2_id: int):
    """Parse Gemma's response for relationship information"""
    try:
        from spacy_llm_tasks.chunk_relationship import ChunkRelationship
        
        lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
        
        relationship_type = "NONE"
        confidence = 0.0
        
        for line in lines:
            if line.startswith("RELATIONSHIP:"):
                relationship_type = line.split(":", 1)[1].strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except ValueError:
                    confidence = 0.0
        
        if relationship_type != "NONE" and confidence > 0:
            return ChunkRelationship(chunk1_id, chunk2_id, confidence, relationship_type)
            
    except Exception as e:
        logger.warning(f"Error parsing relationship response: {e}")
    
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)