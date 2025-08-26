"""
Vercel serverless function for health check
"""
import json
from http.server import BaseHTTPRequestHandler
from _lib import get_parser

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request for health check"""
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Check parser status
            try:
                parser = get_parser()
                parser_ready = parser is not None
            except Exception:
                parser_ready = False
            
            # Create health response
            health_response = {
                "status": "healthy",
                "nlp_ready": True,
                "parser_ready": parser_ready,
                "version": "1.0.0"
            }
            
            # Send response
            self.wfile.write(json.dumps(health_response).encode())
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {"error": f"Health check failed: {str(e)}", "status": "unhealthy"}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(b'')