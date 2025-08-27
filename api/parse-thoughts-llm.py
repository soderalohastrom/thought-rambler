from http.server import BaseHTTPRequestHandler
import json
import re
import time
import sys
import os

# Ensure we don't import the main app by accident
sys.path = [path for path in sys.path if 'backend' not in path or 'api' in path]

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
            enable_llm = request_data.get('enable_llm', False)
            
            if not text:
                self.send_error(400, "Text input cannot be empty")
                return
            
            # Parse thoughts - try LLM enhancement if enabled, fallback to basic
            start_time = time.time()
            
            if enable_llm:
                # Try to use Cloudflare Workers LLM enhancement
                chunks = self.parse_thoughts_llm_enhanced(text, provider, model)
                llm_enhanced = chunks is not None and chunks.get('llm_processed', False)
                
                if not chunks or not llm_enhanced:
                    # Fallback to basic parsing
                    chunks = self.parse_thoughts_basic(text, provider, model)
                    llm_enhanced = False
                else:
                    chunks = chunks.get('chunks', [])
            else:
                # Use basic parsing
                chunks = self.parse_thoughts_basic(text, provider, model)
                llm_enhanced = False
            
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
                    "llm_enhanced": llm_enhanced,
                    "llm_requested": enable_llm,
                    "endpoint": "parse-thoughts-llm",
                    "llm_provider": "cloudflare-workers" if llm_enhanced else "rule-based",
                    "note": "Cloudflare Workers LLM active" if llm_enhanced else "Cloudflare LLM unavailable - using rule-based fallback" if enable_llm else "Basic parsing via LLM endpoint",
                    "average_chunk_length": sum(len(chunk['text']) for chunk in chunks) / len(chunks) if chunks else 0
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Provide detailed error information for debugging
            import traceback
            error_response = {
                "error": f"Error processing text: {str(e)}", 
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(b'')
    
    def parse_thoughts_llm_enhanced(self, text, provider="cloudflare", model="llama-3.1-8b-instruct-fast"):
        """Use Cloudflare Workers LLM for enhanced thought parsing"""
        try:
            import urllib.request
            import urllib.parse
            
            # Cloudflare endpoint for thought rambling
            cloudflare_url = "https://huihui-cognee-processor.scott-c93.workers.dev/api/ramble-thoughts"
            
            # Prepare request data matching Cloudflare API format
            request_data = {
                "text": text,
                "mode": "split_and_group",
                "context": "general",
                "options": {}
            }
            
            # Convert to JSON
            json_data = json.dumps(request_data).encode('utf-8')
            
            # Create request
            req = urllib.request.Request(
                cloudflare_url,
                data=json_data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'ThoughtRambler/1.0'
                }
            )
            
            # Make request with timeout
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    response_data = json.loads(response.read().decode('utf-8'))
                    
                    if response_data.get('success'):
                        # Transform Cloudflare response to our format
                        thought_groups = response_data.get('thought_groups', [])
                        
                        # Convert thought groups to our chunk format
                        chunks = []
                        for i, group in enumerate(thought_groups):
                            # Extract keywords from the text (simple approach)
                            text = group.get('combined_text', '')
                            keywords = []
                            
                            # Extract meaningful words as keywords
                            import re
                            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
                            stop_words = {'the', 'and', 'but', 'for', 'with', 'this', 'that', 'was', 'are', 'have', 'you', 'they', 'she', 'her', 'his', 'him'}
                            keywords = [w for w in words if w not in stop_words][:3]
                            
                            chunks.append({
                                'id': group.get('id', i + 1),
                                'text': text,
                                'confidence': group.get('confidence', 0.85),
                                'start_char': 0,  # Cloudflare doesn't provide char positions
                                'end_char': len(text),
                                'topic_keywords': keywords,
                                'sentiment': group.get('emotional_tone', 'neutral').lower(),
                                'theme': group.get('theme', 'general'),
                                'original_segments': group.get('original_segments', []),
                                'llm_enhanced': True
                            })
                        
                        return {
                            'chunks': chunks,
                            'llm_processed': True,
                            'processing_time': response_data.get('processing_time', 0),
                            'cloudflare_response': True,
                            'model_used': response_data.get('model_used', model),
                            'coherence_score': response_data.get('analysis', {}).get('coherence_score', 0.85)
                        }
                    else:
                        # Cloudflare request failed
                        return None
                        
            except Exception as e:
                # Network or timeout error
                return None
                
        except Exception:
            # Any other error - fallback gracefully
            return None
    
    def parse_relationship_response(self, response, chunk1_id, chunk2_id):
        """Parse Gemma's relationship response"""
        try:
            # This would need the ChunkRelationship class - simplified for now
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
                # Return a simple dict instead of the class for now
                return {
                    'chunk1_id': chunk1_id,
                    'chunk2_id': chunk2_id,
                    'confidence': confidence,
                    'relationship_type': relationship_type
                }
                
        except Exception:
            pass
        
        return None
    
    def parse_thoughts_basic(self, text, provider="openai", model="gpt-3.5-turbo"):
        """Basic rule-based thought parsing (same as regular endpoint)"""
        
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
        
        sentences = [s for s in result if len(s.strip()) > 10]
        
        # Create chunks with simple analysis
        chunks = []
        current_chunk = []
        
        transition_markers = {
            'temporal': ['then', 'next', 'after', 'before', 'meanwhile', 'now', 'later'],
            'logical': ['but', 'however', 'although', 'though', 'nevertheless', 'anyway'],
            'additive': ['also', 'additionally', 'furthermore', 'moreover'],
            'topic_shift': ['speaking of', 'by the way', 'oh', 'wait', 'actually', 'I mean'],
            'decision': ['I should', 'I need to', 'I have to', 'let me'],
            'memory': ['I remember', 'I forgot', 'I was thinking', 'I realized']
        }
        
        for i, sentence in enumerate(sentences):
            should_split = False
            sentence_lower = sentence.lower()
            
            # Check for transition markers
            for category, markers in transition_markers.items():
                for marker in markers:
                    if sentence_lower.startswith(marker) or f' {marker} ' in sentence_lower:
                        should_split = True
                        break
                if should_split:
                    break
            
            # Check for other splitting conditions
            if '?' in sentence or len(sentence.split()) > 15:
                should_split = True
            
            if i > 0 and should_split and current_chunk:
                # Finalize current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'id': len(chunks) + 1,
                    'text': chunk_text,
                    'confidence': 0.85,
                    'start_char': 0,  # Simplified for now
                    'end_char': len(chunk_text),
                    'topic_keywords': self.extract_keywords(chunk_text),
                    'sentiment': self.analyze_sentiment(chunk_text)
                })
                current_chunk = [sentence]
            else:
                current_chunk.append(sentence)
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'id': len(chunks) + 1,
                'text': chunk_text,
                'confidence': 0.85,
                'start_char': 0,
                'end_char': len(chunk_text),
                'topic_keywords': self.extract_keywords(chunk_text),
                'sentiment': self.analyze_sentiment(chunk_text)
            })
        
        return chunks
    
    def analyze_sentiment(self, text):
        """Basic sentiment analysis"""
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
    
    def extract_keywords(self, text):
        """Extract important keywords from text"""
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'about', 'i', 'me', 'my', 'we', 'you', 'they', 'it', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'did', 'will', 'would', 'could', 'should', 'can', 'this', 'that', 'these', 'those'}
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = {}
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:3]]
        
        # Add capitalized words (names/places)
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', text)
        for word in capitalized[:2]:
            if word.lower() not in stop_words and word.lower() not in [k.lower() for k in keywords]:
                keywords.append(word)
        
        return keywords[:5]