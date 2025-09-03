"""
New API endpoint for intelligent text triage
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import asyncio

from triage import TextTriageSystem, URLInferenceEngine, GibberishDetector
from app import SimpleThoughtParser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/triage", tags=["triage"])

# Request/Response models
class TriageRequest(BaseModel):
    text: str
    mode: str = "full"  # full, quick, urls_only
    enable_llm: bool = False
    
class TriageResponse(BaseModel):
    thoughts: List[Dict[str, Any]]
    urls: List[Dict[str, Any]]
    todos: List[Dict[str, Any]]
    quarantine: List[Dict[str, Any]]
    salvaged: List[Dict[str, Any]]
    summary: Dict[str, Any]
    processing_log: List[Dict[str, Any]]

# Initialize systems
thought_parser = SimpleThoughtParser()
triage_system = TextTriageSystem(thought_parser=thought_parser)

@router.post("/process", response_model=TriageResponse)
async def process_text_triage(request: TriageRequest):
    """
    Process text through intelligent triage system
    Categorizes into: thoughts, URLs, TODOs, and quarantine
    """
    try:
        logger.info(f"Processing triage request: {len(request.text)} chars, mode: {request.mode}")
        
        # Process the text dump
        results = await triage_system.process_text_dump(request.text)
        
        logger.info(f"Triage complete: {results['summary']}")
        
        return TriageResponse(**results)
        
    except Exception as e:
        logger.error(f"Triage processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-quality")
async def analyze_text_quality(text: str):
    """
    Analyze text quality without full processing
    Useful for real-time feedback
    """
    detector = GibberishDetector()
    analysis = detector.analyze(text)
    return analysis

@router.post("/infer-url")
async def infer_url_endpoint(description: str):
    """
    Infer URL from vague description
    """
    engine = URLInferenceEngine()
    
    # Check if it's even a URL description
    if not engine.might_be_url_description(description):
        return {
            "url": "",
            "confidence": "none",
            "explanation": "Does not appear to be describing a website"
        }
    
    result = await engine.infer_url(description)
    return result

@router.get("/stats")
async def get_triage_stats():
    """
    Get processing statistics
    """
    return {
        "stats": triage_system.get_stats(),
        "quarantine_count": len(triage_system.quarantine)
    }

@router.delete("/quarantine")
async def clear_quarantine():
    """
    Clear quarantine and return items
    """
    items = triage_system.clear_quarantine()
    return {
        "cleared": len(items),
        "items": items
    }

# Test endpoint with sample data
@router.get("/test-sample")
async def test_with_sample():
    """
    Test triage with sample SMS-like dump
    """
    sample_text = """
need milk and eggs

https://amazon.com/dp/B08XYZ123

that hammock site we looked at yesterday

asdflkjasdf

meeting at 3pm conf room 2 with Sarah about Q4 projections

reddit.com/r/woodworking/comments/abc123

don't forget to call mom about thanksgiving

blue bird social media thing has the news

Remember to pay electric bill by Friday!!!

kelleherinternational.com careers page

jjjjjjjjjjjjj

I should really update my resume this weekend

```
    
    results = await triage_system.process_text_dump(sample_text)
    return results
