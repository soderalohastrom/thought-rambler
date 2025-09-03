"""
Vercel serverless function for text triage processing
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback

# Add backend to path so we can import triage modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Set CORS headers first
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Read request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            text = request_data.get('text', '')
            
            # Simple triage without importing complex modules
            # This is a simplified version for Vercel
            result = self.simple_triage(text)
            
            # Send response
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            # Log the full error
            error_trace = traceback.format_exc()
            print(f"Error in triage-process: {error_trace}")
            
            error_response = {
                "error": f"Error processing triage: {str(e)}",
                "trace": error_trace,
                "thoughts": [],
                "urls": [],
                "todos": [],
                "quarantine": [],
                "salvaged": [],
                "summary": {
                    "total_chunks": 0,
                    "quality_metrics": {"clean_ratio": 0, "url_inference_ratio": 0},
                    "breakdown": {},
                    "recommendations": ["Error occurred during processing"]
                }
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def simple_triage(self, text):
        """Simplified triage for Vercel environment"""
        import re
        
        # Split into chunks
        chunks = text.split('\n')
        chunks = [c.strip() for c in chunks if c.strip()]
        
        thoughts = []
        urls = []
        todos = []
        quarantine = []
        
        # Simple patterns
        url_pattern = r'(?:https?://)?(?:www\.)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
        todo_patterns = [
            r'\b(?:need to|have to|should|must)\s+',
            r'\b(?:todo|task|reminder):\s*',
            r'\b(?:don\'t forget|remember to)\s+'
        ]
        
        for chunk in chunks:
            chunk_lower = chunk.lower()
            
            # Check for URLs
            if re.search(url_pattern, chunk):
                urls.append({
                    'category': 'url',
                    'type': 'explicit',
                    'url': chunk,
                    'original_text': chunk,
                    'confidence': 'high'
                })
            # Check for TODOs
            elif any(re.search(pattern, chunk_lower) for pattern in todo_patterns):
                urgency = 'high' if any(word in chunk_lower for word in ['urgent', 'asap', '!!!']) else 'medium'
                todos.append({
                    'category': 'todo',
                    'action': chunk,
                    'urgency': urgency,
                    'original_text': chunk
                })
            # Check for gibberish (very simple)
            elif len(chunk) < 3 or chunk.count(chunk[0]) == len(chunk):
                quarantine.append({
                    'category': 'gibberish',
                    'original_text': chunk,
                    'issues': ['too_short' if len(chunk) < 3 else 'repetitive']
                })
            # Otherwise it's a thought
            else:
                thoughts.append({
                    'category': 'thought',
                    'original_text': chunk
                })
        
        # Build summary
        total_chunks = len(chunks)
        clean_chunks = len(thoughts) + len(urls) + len(todos)
        
        return {
            'thoughts': thoughts,
            'urls': urls,
            'todos': todos,
            'quarantine': quarantine,
            'salvaged': [],
            'summary': {
                'total_chunks': total_chunks,
                'quality_metrics': {
                    'clean_ratio': clean_chunks / total_chunks if total_chunks > 0 else 0,
                    'url_inference_ratio': 0
                },
                'breakdown': {
                    'thoughts': len(thoughts),
                    'urls': len(urls),
                    'todos': len(todos),
                    'quarantine': len(quarantine)
                },
                'recommendations': []
            },
            'processing_log': []
        }
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
