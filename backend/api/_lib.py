"""
Shared library for thought parsing functionality
"""
import re
import logging
from typing import List, Dict, Any
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request/Response models
class ThoughtParseRequest(BaseModel):
    text: str
    provider: str = "openai"  # openai, anthropic, etc.
    model: str = "gpt-3.5-turbo"

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


# Initialize global parser instance
parser = None

def get_parser():
    """Get or initialize the parser instance"""
    global parser
    if parser is None:
        parser = SimpleThoughtParser()
        logger.info("Thought parser initialized successfully")
    return parser