"""
Text Triage System - Main orchestrator
Intelligently routes text through appropriate processing pipelines
"""

import re
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .gibberish_detector import GibberishDetector
from .url_inference import URLInferenceEngine

logger = logging.getLogger(__name__)

class TextTriageSystem:
    """
    Intelligent text routing system that categorizes and processes text chunks
    Routes to: thoughts, URLs, TODOs, or quarantine
    """
    
    def __init__(self, thought_parser=None):
        self.gibberish_detector = GibberishDetector()
        self.url_engine = URLInferenceEngine()
        self.thought_parser = thought_parser  # Will be injected from main app
        
        # Statistics tracking
        self.stats = {
            'total_processed': 0,
            'thoughts': 0,
            'urls_explicit': 0,
            'urls_inferred': 0,
            'todos': 0,
            'gibberish': 0,
            'salvaged': 0
        }
        
        # Quarantine storage
        self.quarantine = []
        
        # TODO patterns
        self.todo_patterns = [
            r'\b(need to|have to|should|must)\s+\w+',
            r'\b(don\'t forget|remember to|make sure)\s+\w+',
            r'\b(todo|task|reminder):\s*.+',
            r'\b(call|email|text|message|contact)\s+\w+',
            r'\b(buy|get|pick up|order)\s+\w+',
            r'\b(schedule|book|arrange|plan)\s+\w+',
            r'\b(pay|send|submit|file)\s+\w+'
        ]
    
    async def process_text_dump(self, text: str) -> Dict:
        """
        Process a large text dump (like SMS messages)
        Splits and categorizes each chunk intelligently
        """
        # Split text into chunks (by newlines, periods, or SMS-like patterns)
        chunks = self._split_into_chunks(text)
        
        results = {
            'thoughts': [],
            'urls': [],
            'todos': [],
            'quarantine': [],
            'salvaged': [],
            'summary': {},
            'processing_log': []
        }
        
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if not chunk:
                continue
            
            # Process each chunk
            chunk_result = await self.process_chunk(chunk)
            
            # Log the processing
            results['processing_log'].append({
                'chunk_index': i,
                'original': chunk[:50] + '...' if len(chunk) > 50 else chunk,
                'category': chunk_result['category'],
                'confidence': chunk_result.get('confidence', 'N/A')
            })
            
            # Route to appropriate bucket
            if chunk_result['category'] == 'thought':
                results['thoughts'].extend(chunk_result.get('processed', []))
            elif chunk_result['category'] == 'url':
                results['urls'].append(chunk_result)
            elif chunk_result['category'] == 'todo':
                results['todos'].append(chunk_result)
            elif chunk_result['category'] == 'gibberish':
                results['quarantine'].append(chunk_result)
            elif chunk_result['category'] == 'salvaged':
                results['salvaged'].append(chunk_result)
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        
        return results
    
    async def process_chunk(self, chunk: str) -> Dict:
        """
        Process a single text chunk through the triage pipeline
        """
        self.stats['total_processed'] += 1
        
        # Step 1: Check for explicit URLs
        explicit_urls = self.url_engine.extract_explicit_urls(chunk)
        if explicit_urls:
            self.stats['urls_explicit'] += 1
            return {
                'category': 'url',
                'type': 'explicit',
                'urls': explicit_urls,
                'original_text': chunk,
                'confidence': 'high',
                'timestamp': datetime.now().isoformat()
            }
        
        # Step 2: Gibberish detection
        quality_analysis = self.gibberish_detector.analyze(chunk)
        
        if quality_analysis['classification'] == 'gibberish':
            self.stats['gibberish'] += 1
            self.quarantine.append({
                'text': chunk,
                'reason': quality_analysis['issues'],
                'timestamp': datetime.now().isoformat()
            })
            return {
                'category': 'gibberish',
                'quality_score': quality_analysis['quality_score'],
                'issues': quality_analysis['issues'],
                'original_text': chunk,
                'timestamp': datetime.now().isoformat()
            }
        
        # Step 3: Check if salvageable
        if quality_analysis['classification'] == 'salvageable':
            salvaged_parts = quality_analysis['salvageable_parts']
            if salvaged_parts:
                self.stats['salvaged'] += 1
                return {
                    'category': 'salvaged',
                    'salvaged_parts': salvaged_parts,
                    'original_text': chunk,
                    'issues': quality_analysis['issues'],
                    'quality_score': quality_analysis['quality_score']
                }
        
        # Step 4: Check for TODO patterns
        todo_match = self._detect_todo(chunk)
        if todo_match:
            self.stats['todos'] += 1
            return {
                'category': 'todo',
                'action': todo_match['action'],
                'urgency': todo_match['urgency'],
                'original_text': chunk,
                'confidence': todo_match['confidence'],
                'timestamp': datetime.now().isoformat()
            }
        
        # Step 5: Check for URL inference
        if self.url_engine.might_be_url_description(chunk):
            inferred = await self.url_engine.infer_url(chunk)
            if inferred['confidence'] != 'none':
                self.stats['urls_inferred'] += 1
                return {
                    'category': 'url',
                    'type': 'inferred',
                    **inferred,
                    'original_text': chunk,
                    'timestamp': datetime.now().isoformat()
                }
        
        # Step 6: Process as thought (if parser available)
        if self.thought_parser:
            self.stats['thoughts'] += 1
            processed = self.thought_parser.parse_thoughts(chunk)
            return {
                'category': 'thought',
                'processed': processed,
                'original_text': chunk,
                'confidence': 'high',
                'timestamp': datetime.now().isoformat()
            }
        
        # Default: Mark as thought for manual processing
        self.stats['thoughts'] += 1
        return {
            'category': 'thought',
            'processed': [{'text': chunk, 'keywords': [], 'sentiment': 'neutral'}],
            'original_text': chunk,
            'confidence': 'medium',
            'timestamp': datetime.now().isoformat()
        }
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """Split text into processable chunks"""
        # First split by double newlines (paragraphs)
        chunks = re.split(r'\n\n+', text)
        
        # Further split long chunks by single newlines or sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > 500:
                # Split by sentences
                sentences = re.split(r'(?<=[.!?])\s+', chunk)
                final_chunks.extend(sentences)
            elif '\n' in chunk:
                # Split by newlines (SMS-like)
                lines = chunk.split('\n')
                final_chunks.extend(lines)
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _detect_todo(self, text: str) -> Optional[Dict]:
        """Detect if text contains a TODO/action item"""
        text_lower = text.lower()
        
        for pattern in self.todo_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Extract the action part
                action_text = text[match.start():]
                
                # Determine urgency
                urgency = 'medium'
                if any(word in text_lower for word in ['urgent', 'asap', 'immediately', 'today']):
                    urgency = 'high'
                elif any(word in text_lower for word in ['eventually', 'sometime', 'maybe']):
                    urgency = 'low'
                
                return {
                    'action': action_text[:100],  # Limit length
                    'urgency': urgency,
                    'confidence': 'high' if len(action_text.split()) > 3 else 'medium'
                }
        
        return None
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate processing summary"""
        return {
            'total_chunks': sum([
                len(results['thoughts']),
                len(results['urls']),
                len(results['todos']),
                len(results['quarantine']),
                len(results['salvaged'])
            ]),
            'breakdown': {
                'thoughts': len(results['thoughts']),
                'urls': len(results['urls']),
                'todos': len(results['todos']),
                'quarantined': len(results['quarantine']),
                'salvaged': len(results['salvaged'])
            },
            'quality_metrics': {
                'clean_ratio': (len(results['thoughts']) + len(results['urls']) + len(results['todos'])) / 
                               max(1, self.stats['total_processed']),
                'salvage_ratio': len(results['salvaged']) / max(1, len(results['quarantine']) + len(results['salvaged'])),
                'url_inference_ratio': self.stats['urls_inferred'] / max(1, self.stats['urls_explicit'] + self.stats['urls_inferred'])
            },
            'recommendations': self._generate_recommendations(results)
        }
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate processing recommendations"""
        recommendations = []
        
        if len(results['quarantine']) > 5:
            recommendations.append("High gibberish count - consider reviewing input source")
        
        if len(results['todos']) > 10:
            recommendations.append("Many TODOs detected - consider task management integration")
        
        if len(results['salvaged']) > 3:
            recommendations.append("Several partially salvageable chunks - manual review recommended")
        
        if self.stats['urls_inferred'] > self.stats['urls_explicit']:
            recommendations.append("Many inferred URLs - verify accuracy manually")
        
        return recommendations
    
    def get_stats(self) -> Dict:
        """Get processing statistics"""
        return self.stats
    
    def clear_quarantine(self) -> List[Dict]:
        """Clear and return quarantine contents"""
        items = self.quarantine.copy()
        self.quarantine.clear()
        return items
