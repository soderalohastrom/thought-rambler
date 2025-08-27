from http.server import BaseHTTPRequestHandler
import json
import time
import sys
import os

# Global log storage for debugging (in-memory for serverless)
debug_logs = []

def add_debug_log(log_entry):
    """Add a debug log entry"""
    global debug_logs
    log_entry['timestamp'] = time.time()
    log_entry['iso_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    debug_logs.append(log_entry)
    
    # Keep only last 50 entries to prevent memory bloat
    if len(debug_logs) > 50:
        debug_logs = debug_logs[-50:]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Return current debug logs
            response = {
                "logs": debug_logs,
                "total_logs": len(debug_logs),
                "server_time": time.time(),
                "server_info": {
                    "endpoint": "/api/debug-logs",
                    "purpose": "Real-time debugging logs for LLM integration",
                    "retention": "Last 50 entries",
                    "note": "Logs are cleared on serverless function restart"
                }
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "error": f"Error fetching debug logs: {str(e)}",
                "type": type(e).__name__
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_POST(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Read and parse request for adding custom log entry
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            log_entry = request_data.get('log_entry', {})
            log_type = request_data.get('type', 'custom')
            
            # Add the log entry
            add_debug_log({
                'type': log_type,
                'source': 'api_client',
                **log_entry
            })
            
            response = {
                "success": True,
                "message": "Log entry added",
                "total_logs": len(debug_logs)
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "error": f"Error adding debug log: {str(e)}",
                "type": type(e).__name__
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(b'')