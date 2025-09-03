"""
Shared NLP Core
Singleton pattern for spaCy pipeline shared between Thought Parser and Text Triage
Optimized for STT (Speech-to-Text) processing
"""

import spacy
from typing import List, Dict, Tuple, Optional
import re
import logging

logger = logging.getLogger(__name__)

class NLPCore:
    """
    Shared NLP processing core using spaCy
    Handles sophisticated text segmentation for both structured and STT inputs
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                # Try to load the model
                cls._instance.nlp = spacy.load("en_core_web_sm")
                cls._instance.model_loaded = True
                logger.info("spaCy model loaded successfully")
            except:
                logger.warning("spaCy model not found, falling back to basic segmentation")
                cls._instance.nlp = None
                cls._instance.model_loaded = False
                
            # Discourse markers common in STT
            cls._instance.discourse_markers = {
                'topic_shift': ['anyway', 'so', 'oh', 'btw', 'by the way', 'also', 'plus'],
                'continuation': ['and', 'then', 'next', 'after that'],
                'contrast': ['but', 'however', 'although', 'though'],
                'filler': ['um', 'uh', 'like', 'you know', 'I mean', 'basically']
            }
            
        return cls._instance
    
    def segment_thoughts(self, text: str, mode: str = 'balanced') -> List[Dict]:
        """
        Intelligently segment text into semantic chunks
        
        Modes:
        - 'strict': One sentence = one thought
        - 'balanced': Group related sentences (default)
        - 'loose': Larger semantic chunks
        """
        if not self.model_loaded:
            return self._basic_segmentation(text)
        
        doc = self.nlp(text)
        thoughts = []
        
        if mode == 'strict':
            # Each sentence is a separate thought
            for sent in doc.sents:
                thoughts.append(self._analyze_sentence(sent))
        
        elif mode == 'balanced':
            # Group related sentences
            current_chunk = []
            current_topic = None
            
            for sent in doc.sents:
                sent_analysis = self._analyze_sentence(sent)
                
                # Check if this is a thought boundary
                if self._is_thought_boundary(sent_analysis, current_topic, current_chunk):
                    if current_chunk:
                        thoughts.append(self._merge_chunk(current_chunk))
                    current_chunk = [sent_analysis]
                    current_topic = self._extract_topic(sent_analysis)
                else:
                    current_chunk.append(sent_analysis)
            
            # Don't forget the last chunk
            if current_chunk:
                thoughts.append(self._merge_chunk(current_chunk))
        
        else:  # loose
            # Larger semantic chunks based on major topic shifts
            current_chunk = []
            
            for sent in doc.sents:
                sent_analysis = self._analyze_sentence(sent)
                
                # Only break on major shifts
                if self._is_major_shift(sent_analysis, current_chunk):
                    if current_chunk:
                        thoughts.append(self._merge_chunk(current_chunk))
                    current_chunk = [sent_analysis]
                else:
                    current_chunk.append(sent_analysis)
            
            if current_chunk:
                thoughts.append(self._merge_chunk(current_chunk))
        
        return thoughts
    
    def _analyze_sentence(self, sent) -> Dict:
        """Extract linguistic features from a sentence"""
        # Find the main verb and subject
        root = sent.root
        subject = None
        verb = root.text if root.pos_ == 'VERB' else None
        
        for token in sent:
            if token.dep_ == 'nsubj':
                subject = token.text
                break
        
        # Extract entities
        entities = [(ent.text, ent.label_) for ent in sent.ents]
        
        # Check for discourse markers
        text_lower = sent.text.lower()
        has_discourse_marker = any(
            marker in text_lower 
            for markers in self.discourse_markers.values() 
            for marker in markers
        )
        
        # Detect if it starts with a discourse marker
        starts_with_marker = False
        for marker_type, markers in self.discourse_markers.items():
            for marker in markers:
                if text_lower.strip().startswith(marker):
                    starts_with_marker = marker_type
                    break
        
        return {
            'text': sent.text.strip(),
            'root': root.text,
            'root_pos': root.pos_,
            'subject': subject,
            'verb': verb,
            'entities': entities,
            'has_discourse_marker': has_discourse_marker,
            'starts_with_marker': starts_with_marker,
            'word_count': len(sent.text.split()),
            'has_question': '?' in sent.text,
            'has_exclamation': '!' in sent.text,
            # STT-specific features
            'has_filler': any(filler in text_lower for filler in self.discourse_markers['filler']),
            'entity_types': list(set(e[1] for e in entities))
        }
    
    def _is_thought_boundary(self, sent_analysis: Dict, current_topic: str, current_chunk: List) -> bool:
        """
        Determine if this sentence starts a new thought
        Optimized for STT where topic shifts are common
        """
        # Always break on explicit topic shift markers
        if sent_analysis['starts_with_marker'] == 'topic_shift':
            return True
        
        # Break on questions after statements
        if sent_analysis['has_question'] and current_chunk:
            last_was_question = current_chunk[-1].get('has_question', False)
            if not last_was_question:
                return True
        
        # Break if subject changes significantly
        if current_topic and sent_analysis['subject']:
            if current_topic != sent_analysis['subject']:
                # But not if it's a pronoun reference
                if sent_analysis['subject'].lower() not in ['he', 'she', 'it', 'they', 'we', 'i']:
                    return True
        
        # Break on entity type changes (e.g., from PERSON to ORG)
        if current_chunk and current_chunk[-1]['entity_types'] != sent_analysis['entity_types']:
            if sent_analysis['entity_types']:  # Only if new sentence has entities
                return True
        
        # Don't break on continuations
        if sent_analysis['starts_with_marker'] == 'continuation':
            return False
        
        # Break if we've accumulated enough content (for long rambles)
        if len(current_chunk) >= 3:
            total_words = sum(s['word_count'] for s in current_chunk)
            if total_words > 50:  # Roughly 2-3 sentences worth
                return True
        
        return False
    
    def _is_major_shift(self, sent_analysis: Dict, current_chunk: List) -> bool:
        """Detect major topic shifts for loose segmentation"""
        if not current_chunk:
            return False
        
        # Only break on strong indicators
        return (
            sent_analysis['starts_with_marker'] == 'topic_shift' or
            (sent_analysis['has_question'] and not current_chunk[-1].get('has_question', False)) or
            (len(current_chunk) > 5)  # Prevent overly long chunks
        )
    
    def _extract_topic(self, sent_analysis: Dict) -> Optional[str]:
        """Extract the main topic (usually the subject or first entity)"""
        if sent_analysis['subject']:
            return sent_analysis['subject']
        if sent_analysis['entities']:
            return sent_analysis['entities'][0][0]
        return None
    
    def _merge_chunk(self, chunk: List[Dict]) -> Dict:
        """Merge multiple sentence analyses into a single thought"""
        merged_text = ' '.join(s['text'] for s in chunk)
        
        # Combine all entities
        all_entities = []
        entity_types = set()
        for s in chunk:
            all_entities.extend(s['entities'])
            entity_types.update(s['entity_types'])
        
        # Find primary subject and verb
        primary_subject = None
        primary_verb = None
        for s in chunk:
            if s['subject'] and not primary_subject:
                primary_subject = s['subject']
            if s['verb'] and not primary_verb:
                primary_verb = s['verb']
        
        return {
            'text': merged_text,
            'sentence_count': len(chunk),
            'word_count': sum(s['word_count'] for s in chunk),
            'primary_subject': primary_subject,
            'primary_verb': primary_verb,
            'entities': all_entities,
            'entity_types': list(entity_types),
            'has_question': any(s['has_question'] for s in chunk),
            'has_exclamation': any(s['has_exclamation'] for s in chunk),
            'has_filler': any(s['has_filler'] for s in chunk),
            # Keep individual sentences for reference
            'sentences': [s['text'] for s in chunk]
        }
    
    def _basic_segmentation(self, text: str) -> List[Dict]:
        """Fallback segmentation without spaCy"""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        thoughts = []
        for sent in sentences:
            if sent.strip():
                thoughts.append({
                    'text': sent.strip(),
                    'sentence_count': 1,
                    'word_count': len(sent.split()),
                    'entities': [],
                    'entity_types': [],
                    'has_question': '?' in sent,
                    'has_exclamation': '!' in sent
                })
        
        return thoughts
    
    def extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """Extract all named entities from text"""
        if not self.model_loaded:
            return []
        
        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]
    
    def get_sentences(self, text: str) -> List[str]:
        """Simple sentence extraction"""
        if not self.model_loaded:
            return re.split(r'(?<=[.!?])\s+', text)
        
        doc = self.nlp(text)
        return [sent.text.strip() for sent in doc.sents]