"""Vercel serverless function for LLM-enhanced thought parsing"""

import json
import time
import re

def handler(request):
    """Main Vercel handler function for LLM-enhanced parsing"""
    # Set CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return ('', 200, headers)
    
    try:
        # Get request data
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                data = {}
        else:
            return (json.dumps({"detail": "Method not allowed"}), 405, headers)
        
        # Validate input
        text = data.get('text', '').strip()
        if not text:
            return (json.dumps({"detail": "Text input cannot be empty"}), 400, headers)
        
        # Extract parameters
        enable_llm = data.get('enable_llm', False)
        provider = data.get('provider', 'openai')
        model = data.get('model', 'gpt-3.5-turbo')
        
        # Process the text (basic parsing for now, LLM enhancement disabled until dependencies resolved)
        start_time = time.time()
        chunks = basic_parse_text(text)
        processing_time = time.time() - start_time
        
        # Build response
        result = {
            "chunks": chunks,
            "total_chunks": len(chunks),
            "processing_time": processing_time,
            "metadata": {
                "input_length": len(text),
                "provider": provider,
                "model": model,
                "llm_enhanced": False,  # Disabled until we resolve dependency issues
                "average_chunk_length": sum(len(chunk['text']) for chunk in chunks) / len(chunks) if chunks else 0,
                "note": "Basic parsing mode - LLM integration in progress"
            }
        }
        
        return (json.dumps(result), 200, headers)
        
    except Exception as e:
        error_response = {"detail": f"Error processing request: {str(e)}"}
        return (json.dumps(error_response), 500, headers)

def basic_parse_text(text: str):
    """Basic text parsing without heavy dependencies"""
    # Basic preprocessing
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Split on sentence boundaries and conjunctions  
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    
    current_pos = 0
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if len(sentence) > 10:  # Filter very short segments
            # Find position in original text
            start_pos = text.find(sentence, current_pos)
            if start_pos == -1:
                start_pos = current_pos
            
            end_pos = start_pos + len(sentence)
            current_pos = end_pos
            
            # Basic keyword extraction
            words = re.findall(r'\b[a-zA-Z]{3,}\b', sentence.lower())
            stop_words = {'the', 'and', 'but', 'for', 'with', 'this', 'that', 'was', 'are', 'have', 'you', 'they', 'she', 'her', 'his', 'him'}
            keywords = [w for w in words if w not in stop_words][:3]
            
            # Basic sentiment analysis
            positive_words = ['good', 'great', 'happy', 'excited', 'love', 'amazing', 'wonderful', 'excellent']
            negative_words = ['bad', 'terrible', 'sad', 'angry', 'hate', 'awful', 'horrible', 'frustrated']
            
            sentence_lower = sentence.lower()
            pos_count = sum(1 for w in positive_words if w in sentence_lower)
            neg_count = sum(1 for w in negative_words if w in sentence_lower)
            
            sentiment = 'positive' if pos_count > neg_count else 'negative' if neg_count > pos_count else 'neutral'
            
            chunks.append({
                'id': i + 1,
                'text': sentence,
                'confidence': 0.8,  # Basic confidence score
                'start_char': start_pos,
                'end_char': end_pos,
                'topic_keywords': keywords,
                'sentiment': sentiment
            })
    
    return chunks

# For local testing
if __name__ == "__main__":
    # Mock request object
    class MockRequest:
        def __init__(self, method='POST', json_data=None):
            self.method = method
            self._json_data = json_data or {}
            
        def get_json(self):
            return self._json_data
    
    test_request = MockRequest('POST', {
        'text': 'I was thinking about getting a new car. Then I realized I should probably save money instead. Maybe I should just fix my current car and keep using it for another year.',
        'enable_llm': True,
        'provider': 'gemma',
        'model': 'gemma-270m'
    })
    
    response_body, status_code, headers = handler(test_request)
    print(f"Status: {status_code}")
    print(f"Headers: {headers}")
    print(f"Body: {json.dumps(json.loads(response_body), indent=2)}")