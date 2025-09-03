"""
Gibberish Detection Module
Identifies and quarantines unintelligible text chunks
"""

import re
import string
from typing import Dict, List, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class GibberishDetector:
    """Detects various forms of gibberish, malformed text, and low-quality input"""
    
    def __init__(self):
        # Gibberish pattern definitions
        self.patterns = {
            'encoding_errors': re.compile(r'[�\ufffd]{2,}'),  # Unicode replacement chars
            'excessive_special': re.compile(r'^[^a-zA-Z0-9\s]{10,}$'),  # Just symbols
            'number_soup': re.compile(r'^[\d\s\.\-\(\)]+$'),  # Just numbers/formatting
            'single_char_repeat': re.compile(r'^(.)\1{5,}$'),  # "aaaaaaa"
            'random_caps': re.compile(r'^(?:[A-Z]{1,2}[a-z]{0,2}){10,}$'),  # "AsDfGhJkL"
            'keyboard_smash': re.compile(r'^[asdfghjkl;]{8,}$|^[qwerty]{8,}$'),  # Frustration
            'truncated_base64': re.compile(r'^[A-Za-z0-9+/]{20,}={0,2}$'),  # Broken encoding
            'excessive_punctuation': re.compile(r'^[!?.,:;]{5,}')  # "!!!???...."
        }
        
        # Common English words for coherence check
        self.common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
            'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go'
        }
        
        # Quality score thresholds
        self.thresholds = {
            'high_quality': 0.7,    # Good, coherent text
            'salvageable': 0.4,      # Has issues but recoverable
            'gibberish': 0.2         # Pre-trash purgatory
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Comprehensive text quality analysis
        Returns dict with quality score, issues, and recommendations
        """
        if not text or not text.strip():
            return {
                'quality_score': 0.0,
                'classification': 'empty',
                'issues': ['Empty or whitespace-only input'],
                'salvageable_parts': [],
                'recommendation': 'discard'
            }
        
        text = text.strip()
        issues = []
        scores = []
        
        # Check for pattern-based gibberish
        pattern_result = self._check_patterns(text)
        if pattern_result['matches']:
            issues.extend(pattern_result['matches'])
            scores.append(0.0)  # Pattern match = likely gibberish
        else:
            scores.append(1.0)
        
        # Check word coherence
        coherence_score = self._calculate_word_coherence(text)
        scores.append(coherence_score)
        if coherence_score < 0.3:
            issues.append('Low word coherence')
        
        # Check character distribution
        char_diversity = self._calculate_character_diversity(text)
        scores.append(char_diversity)
        if char_diversity < 0.3:
            issues.append('Poor character diversity')
        
        # Check for sentence structure
        structure_score = self._analyze_structure(text)
        scores.append(structure_score)
        if structure_score < 0.3:
            issues.append('No clear sentence structure')
        
        # Check for repetition
        repetition_score = 1.0 - self._calculate_repetition(text)
        scores.append(repetition_score)
        if repetition_score < 0.5:
            issues.append('Excessive repetition')
        
        # Calculate overall quality score
        quality_score = sum(scores) / len(scores) if scores else 0.0
        
        # Attempt to salvage parts if quality is low but not hopeless
        salvageable_parts = []
        if 0.2 < quality_score < 0.7:
            salvageable_parts = self._extract_salvageable_parts(text)
        
        # Classify based on score
        if quality_score >= self.thresholds['high_quality']:
            classification = 'high_quality'
            recommendation = 'process'
        elif quality_score >= self.thresholds['salvageable']:
            classification = 'salvageable'
            recommendation = 'review'
        else:
            classification = 'gibberish'
            recommendation = 'quarantine'
        
        return {
            'quality_score': round(quality_score, 3),
            'classification': classification,
            'issues': issues,
            'salvageable_parts': salvageable_parts,
            'recommendation': recommendation,
            'original_text': text[:100] + '...' if len(text) > 100 else text
        }
    
    def _check_patterns(self, text: str) -> Dict:
        """Check for known gibberish patterns"""
        matches = []
        for pattern_name, pattern in self.patterns.items():
            if pattern.search(text):
                matches.append(f'Pattern: {pattern_name}')
        return {'matches': matches}
    
    def _calculate_word_coherence(self, text: str) -> float:
        """Calculate ratio of recognizable English words"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if not words:
            return 0.0
        
        recognized = sum(1 for word in words if word in self.common_words or len(word) <= 2)
        return min(recognized / len(words), 1.0)
    
    def _calculate_character_diversity(self, text: str) -> float:
        """Measure character type diversity"""
        if not text:
            return 0.0
        
        has_alpha = bool(re.search(r'[a-zA-Z]', text))
        has_space = bool(re.search(r'\s', text))
        
        # Calculate ratios
        alpha_ratio = len(re.findall(r'[a-zA-Z]', text)) / len(text)
        digit_ratio = len(re.findall(r'\d', text)) / len(text)
        special_ratio = len(re.findall(r'[^a-zA-Z0-9\s]', text)) / len(text)
        
        # Good text has mostly letters with some spaces
        if has_alpha and has_space and 0.5 < alpha_ratio < 0.95:
            return 1.0
        elif has_alpha and alpha_ratio > 0.3:
            return 0.7
        elif special_ratio > 0.5 or digit_ratio > 0.7:
            return 0.2
        else:
            return 0.4
    
    def _analyze_structure(self, text: str) -> float:
        """Check for basic sentence structure indicators"""
        # Look for sentence patterns
        has_capital = bool(re.search(r'^[A-Z]', text))
        has_period = bool(re.search(r'\.$', text))
        has_words = len(text.split()) > 2
        
        # Check for verb-like words (simple heuristic)
        verb_patterns = r'\b(is|are|was|were|have|has|had|do|does|did|will|would|could|should|can|may|might|must|shall|need|want|going|make|take|get|give|go|come|see|know|think|say|tell)\b'
        has_verb = bool(re.search(verb_patterns, text.lower()))
        
        score = 0.0
        if has_words: score += 0.4
        if has_verb: score += 0.3
        if has_capital: score += 0.15
        if has_period: score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_repetition(self, text: str) -> float:
        """Calculate repetition score (higher = more repetition)"""
        if len(text) < 10:
            return 0.0
        
        # Check character-level repetition
        chars = list(text)
        char_counts = Counter(chars)
        max_repeat = max(char_counts.values())
        char_repetition = max_repeat / len(chars)
        
        # Check word-level repetition
        words = text.lower().split()
        if words:
            word_counts = Counter(words)
            max_word_repeat = max(word_counts.values())
            word_repetition = max_word_repeat / len(words)
        else:
            word_repetition = 0.0
        
        return max(char_repetition, word_repetition)
    
    def _extract_salvageable_parts(self, text: str) -> List[str]:
        """Try to extract meaningful parts from partially gibberish text"""
        salvageable = []
        
        # Split by common delimiters and check each part
        parts = re.split(r'[;,\n\r|]+', text)
        
        for part in parts:
            part = part.strip()
            if len(part) < 5:
                continue
            
            # Simple quality check without recursion
            coherence = self._calculate_word_coherence(part)
            structure = self._analyze_structure(part)
            
            # If part seems reasonable, save it
            if coherence > 0.5 or structure > 0.5:
                salvageable.append(part)
        
        # Also try extracting sentences
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and sentence not in salvageable:
                if self._calculate_word_coherence(sentence) > 0.5:
                    salvageable.append(sentence)
        
        return salvageable
