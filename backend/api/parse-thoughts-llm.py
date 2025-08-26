from http.server import BaseHTTPRequestHandler
import json
import re
import time
import logging
import os
import sys
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import spacy
    from spacy.tokens import Doc
    from spacy_llm.util import assemble
    
    # Import our custom components
    from models.gemma_loader import get_gemma_model, GemmaModel
    from spacy_llm_tasks.chunk_relationship import merge_related_chunks, ChunkRelationship
    
    SPACY_AVAILABLE = True
except ImportError as e:
    SPACY_AVAILABLE = False
    logging.warning(f"spacy-llm components not available: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Read and parse request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            text = request_data.get('text', '').strip()
            provider = request_data.get('provider', 'openai')
            model = request_data.get('model', 'gpt-3.5-turbo')
            enable_llm = request_data.get('enable_llm', True)
            
            if not text:
                self.send_error(400, "Text input cannot be empty")
                return
            
            # Parse thoughts with LLM enhancement
            start_time = time.time()
            
            if SPACY_AVAILABLE and enable_llm:
                chunks = self.parse_thoughts_with_llm(text, provider, model)
            else:
                # Fallback to basic parsing
                logger.info("Using fallback basic parsing (spacy-llm not available or disabled)")
                chunks = self.parse_thoughts_basic(text, provider, model)
            
            processing_time = time.time() - start_time
            
            # Create response
            response = {
                "chunks": chunks,
                "total_chunks": len(chunks),
                "processing_time": processing_time,
                "metadata": {
                    "input_length": len(text),
                    "provider": provider,
                    "model": model,
                    "llm_enhanced": SPACY_AVAILABLE and enable_llm,
                    "average_chunk_length": sum(len(chunk['text']) for chunk in chunks) / len(chunks) if chunks else 0
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            logger.error(f"Error in LLM processing: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {"error": f"Error processing text with LLM: {str(e)}"}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(b'')
    
    def parse_thoughts_with_llm(self, text: str, provider: str = "openai", model: str = "gpt-3.5-turbo") -> List[Dict[str, Any]]:
        """Parse thoughts using spacy-llm with Gemma for chunk relationship detection"""
        try:
            logger.info("Starting spacy-llm enhanced parsing")
            
            # Step 1: Basic spaCy processing to get initial chunks
            basic_chunks = self.parse_thoughts_basic(text, provider, model)
            
            if len(basic_chunks) < 2:
                logger.info("Less than 2 chunks, no relationship detection needed")
                return basic_chunks
            
            # Step 2: Use spacy-llm for relationship detection
            try:
                enhanced_chunks = self.detect_and_merge_relationships(basic_chunks, text)
                logger.info(f"LLM enhancement completed: {len(basic_chunks)} -> {len(enhanced_chunks)} chunks")
                return enhanced_chunks
            except Exception as e:
                logger.warning(f"LLM relationship detection failed, using basic chunks: {e}")
                return basic_chunks
                
        except Exception as e:
            logger.error(f"Error in LLM parsing: {e}")
            # Fallback to basic parsing
            return self.parse_thoughts_basic(text, provider, model)
    
    def detect_and_merge_relationships(self, chunks: List[Dict[str, Any]], original_text: str) -> List[Dict[str, Any]]:
        """Use Gemma to detect relationships between chunks and merge related ones"""
        
        if len(chunks) < 2:
            return chunks
            
        try:
            # Get Gemma model
            gemma = get_gemma_model()
            
            if not gemma.is_available():
                logger.warning("Gemma model not available, skipping relationship detection")
                return chunks
            
            # Analyze relationships between chunks
            relationships = []
            
            for i, chunk1 in enumerate(chunks):
                for j in range(i + 1, min(i + 4, len(chunks))):  # Check within 3-chunk window
                    chunk2 = chunks[j]
                    
                    # Create prompt for relationship detection
                    prompt = self.create_relationship_prompt(chunk1['text'], chunk2['text'])
                    
                    try:
                        response = gemma([prompt])[0]
                        relationship = self.parse_relationship_response(response, i, j)
                        
                        if relationship and relationship.confidence >= 0.7:
                            relationships.append(relationship)
                            logger.info(f"Found relationship between chunks {i} and {j}: {relationship.relationship_type} (confidence: {relationship.confidence})")
                    
                    except Exception as e:
                        logger.warning(f"Failed to analyze chunk relationship {i}-{j}: {e}")
                        continue
            
            # Merge related chunks
            if relationships:
                merged_chunks = merge_related_chunks(chunks, relationships)
                return merged_chunks
            else:
                logger.info("No significant relationships found")
                return chunks
                
        except Exception as e:
            logger.error(f"Error in relationship detection: {e}")
            return chunks
    
    def create_relationship_prompt(self, chunk1_text: str, chunk2_text: str) -> str:
        """Create a prompt for Gemma to analyze chunk relationships"""
        return f"""Analyze if these two text segments are related:

Segment 1: "{chunk1_text}"
Segment 2: "{chunk2_text}"

Consider if they discuss:
- Same topic or subject
- Same person or entity
- Same event or situation
- Related cause and effect
- Temporal sequence

Respond with:
RELATIONSHIP: [SAME_TOPIC|SAME_PERSON|SAME_EVENT|CAUSE_EFFECT|TEMPORAL|NONE]
CONFIDENCE: [0.0 to 1.0]
REASONING: [brief explanation]

Example:
RELATIONSHIP: SAME_PERSON
CONFIDENCE: 0.95
REASONING: Both segments discuss the same boss and her behavior."""

    def parse_relationship_response(self, response: str, chunk1_id: int, chunk2_id: int) -> Optional[ChunkRelationship]:
        """Parse Gemma's response to extract relationship information"""
        try:
            lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
            
            relationship_type = "NONE"
            confidence = 0.0
            
            for line in lines:
                if line.startswith("RELATIONSHIP:"):
                    relationship_type = line.split(":", 1)[1].strip()
                elif line.startswith("CONFIDENCE:"):
                    confidence_str = line.split(":", 1)[1].strip()
                    try:
                        confidence = float(confidence_str)
                    except ValueError:
                        confidence = 0.0
            
            if relationship_type != "NONE" and confidence > 0:
                return ChunkRelationship(chunk1_id, chunk2_id, confidence, relationship_type)
                
        except Exception as e:
            logger.warning(f"Error parsing relationship response: {e}")
        
        return None
    
    def parse_thoughts_basic(self, text: str, provider: str = "openai", model: str = "gpt-3.5-turbo") -> List[Dict[str, Any]]:
        """Basic thought parsing (fallback when LLM is not available)"""
        
        # Preprocessing
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'\b(um|uh|er|ah)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text)
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Further split on conjunctions
        result = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            parts = re.split(r'\b(and|but|so|then)\b', sentence)
            current_part = ""
            for part in parts:
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
        
        # Create chunks with metadata
        chunks = []
        for i, chunk_text in enumerate(result):
            if chunk_text:
                # Basic keyword extraction
                keywords = [word.lower() for word in re.findall(r'\b[a-zA-Z]{3,}\b', chunk_text)][:3]
                
                chunk = {
                    'id': i + 1,
                    'text': chunk_text,
                    'confidence': 0.85,
                    'start_char': 0,  # Simplified for basic parsing
                    'end_char': len(chunk_text),
                    'topic_keywords': keywords,
                    'sentiment': 'neutral'
                }
                chunks.append(chunk)
        
        return chunks