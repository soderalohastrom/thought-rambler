"""
Vercel serverless function for parsing thought rambles
"""
import json
import time
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from _lib import get_parser, ThoughtParseRequest, ThoughtParseResponse, ThoughtChunk

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request for thought parsing"""
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON request
            try:
                request_data = json.loads(post_data.decode('utf-8'))
                request = ThoughtParseRequest(**request_data)
            except Exception as e:
                error_response = {"error": f"Invalid request data: {str(e)}"}
                self.wfile.write(json.dumps(error_response).encode())
                return
            
            # Validate input
            if not request.text.strip():
                error_response = {"error": "Text input cannot be empty"}
                self.wfile.write(json.dumps(error_response).encode())
                return
            
            # Get parser and parse thoughts
            parser = get_parser()
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
            
            # Send response
            response_json = response.model_dump()
            self.wfile.write(json.dumps(response_json).encode())
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {"error": f"Error processing text: {str(e)}"}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(b'')