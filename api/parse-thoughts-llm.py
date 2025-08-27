"""Vercel serverless function for LLM-enhanced thought parsing using Gemma 270M"""

import json
import logging
import time
import sys
import os
from typing import Dict, Any, List

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configure logging for serverless environment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(event, context):
    """Vercel serverless function handler for LLM-enhanced parsing"""
    try:
        # Handle CORS preflight
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Content-Type": "application/json"
        }
        
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Parse request body
        if isinstance(event.get('body'), str):
            request_data = json.loads(event['body'])
        else:
            request_data = event.get('body', {})
        
        # Validate required fields
        text = request_data.get('text', '').strip()
        if not text:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({"detail": "Text input cannot be empty"})
            }
        
        # Extract parameters
        provider = request_data.get('provider', 'openai')
        model = request_data.get('model', 'gpt-3.5-turbo')
        enable_llm = request_data.get('enable_llm', False)
        
        logger.info(f"Processing LLM request: enable_llm={enable_llm}, provider={provider}")
        
        # Initialize parser
        from app import get_parser
        current_parser = get_parser()
        
        if not current_parser:
            return {
                'statusCode': 503,
                'headers': headers,
                'body': json.dumps({"detail": "Parser not initialized. Please ensure spaCy model is loaded."})
            }
        
        start_time = time.time()
        enhanced_chunks = []
        llm_available = False
        
        # Try LLM-enhanced parsing if enabled
        if enable_llm:
            try:
                enhanced_chunks = parse_with_gemma_llm(text, provider, model, current_parser)
                if enhanced_chunks:
                    llm_available = True
                    logger.info("Successfully used Gemma LLM for enhancement")
                else:
                    logger.warning("Gemma LLM returned empty results, falling back to basic parsing")
            except Exception as e:
                logger.warning(f"LLM enhancement failed: {e}, falling back to basic parsing")
        
        # Fallback to basic parsing if LLM failed or disabled
        if not enhanced_chunks:
            enhanced_chunks = current_parser.parse_thoughts(text, provider, model)
        
        processing_time = time.time() - start_time
        
        # Build response
        response_data = {
            "chunks": enhanced_chunks,
            "total_chunks": len(enhanced_chunks),
            "processing_time": processing_time,
            "metadata": {
                "input_length": len(text),
                "provider": provider,
                "model": model,
                "llm_enhanced": llm_available and enable_llm,
                "average_chunk_length": sum(len(chunk.get('text', '')) for chunk in enhanced_chunks) / len(enhanced_chunks) if enhanced_chunks else 0
            }
        }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        logger.error(f"Error in LLM parsing handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({"detail": f"Error processing text with LLM: {str(e)}"})
        }

def parse_with_gemma_llm(text: str, provider: str, model: str, parser) -> List[Dict[str, Any]]:
    """Parse thoughts using Gemma 270M model for relationship detection"""
    try:
        # Import Gemma components
        from models.gemma_loader import get_gemma_model
        from spacy_llm_tasks.chunk_relationship import merge_related_chunks, ChunkRelationship
        
        # Step 1: Get basic chunks from rule-based parser
        basic_chunks = parser.parse_thoughts(text, provider, model)
        
        if len(basic_chunks) < 2:
            logger.info("Less than 2 chunks, skipping LLM enhancement")
            return basic_chunks
        
        # Step 2: Initialize Gemma model
        gemma = get_gemma_model()
        if not gemma.is_available():
            logger.warning("Gemma model not available")
            return []
        
        # Step 3: Detect relationships between chunks
        relationships = []
        
        for i, chunk1 in enumerate(basic_chunks):
            # Only check relationships within a sliding window to avoid too many API calls
            for j in range(i + 1, min(i + 4, len(basic_chunks))):
                chunk2 = basic_chunks[j]
                
                # Create relationship analysis prompt
                prompt = create_relationship_prompt(chunk1['text'], chunk2['text'])
                
                try:
                    # Get Gemma's analysis
                    response = gemma([prompt])[0]
                    relationship = parse_relationship_response(response, i, j)
                    
                    if relationship and relationship.confidence >= 0.7:
                        relationships.append(relationship)
                        logger.info(f"Found relationship: {i}-{j} ({relationship.relationship_type}, {relationship.confidence:.2f})")
                
                except Exception as e:
                    logger.warning(f"Failed to analyze relationship {i}-{j}: {e}")
                    continue
        
        # Step 4: Merge related chunks if relationships were found
        if relationships:
            enhanced_chunks = merge_related_chunks(basic_chunks, relationships)
            logger.info(f"Gemma enhancement: {len(basic_chunks)} -> {len(enhanced_chunks)} chunks")
            return enhanced_chunks
        else:
            logger.info("No relationships found, returning original chunks")
            return basic_chunks
            
    except ImportError as e:
        logger.warning(f"Gemma components not available: {e}")
        return []
    except Exception as e:
        logger.error(f"Gemma processing failed: {e}")
        return []

def create_relationship_prompt(chunk1_text: str, chunk2_text: str) -> str:
    """Create a prompt for Gemma to analyze chunk relationships"""
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

# Entry point for Vercel
def main(event, context=None):
    return handler(event, context)

# For local testing
if __name__ == "__main__":
    # Test payload
    test_event = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'text': 'I was thinking about getting a new car, then I realized I should probably save money instead. Maybe I should just fix my current car.',
            'enable_llm': True,
            'provider': 'gemma',
            'model': 'gemma-270m'
        })
    }
    
    result = handler(test_event, None)
    print(json.dumps(result, indent=2))