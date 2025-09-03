"""
URL Inference Engine
Adapted from url-recognizer PoC to work within the thought-rambler system
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, urlunparse
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class URLInferenceEngine:
    """Infers URLs from vague human descriptions and validates them"""
    
    def __init__(self):
        # URL detection triggers
        self.url_triggers = [
            'site', 'website', 'webpage', 'link', 'url', 'domain',
            '.com', '.org', '.net', '.io', '.co', '.edu',
            'http://', 'https://', 'www.',
            'online', 'web app', 'platform', 'portal',
            'that place where', 'the site with', 'the page'
        ]
        
        # Known domain mappings for common descriptions
        self.known_sites = {
            # Social media
            'blue bird': 'twitter.com',
            'x.com': 'x.com',  # Twitter rebrand
            'face book': 'facebook.com',
            'insta': 'instagram.com',
            'reddit': 'reddit.com',
            'linked in': 'linkedin.com',
            'tik tok': 'tiktok.com',
            
            # Shopping
            'amazon': 'amazon.com',
            'ebay': 'ebay.com',
            'etsy': 'etsy.com',
            'alibaba': 'alibaba.com',
            'hammock': ['hammocks.com', 'hammockcompany.com', 'eno.com'],
            
            # Tech
            'github': 'github.com',
            'stack overflow': 'stackoverflow.com',
            'hacker news': 'news.ycombinator.com',
            
            # Video/Media
            'youtube': 'youtube.com',
            'netflix': 'netflix.com',
            'spotify': 'spotify.com',
            
            # Search
            'google': 'google.com',
            'bing': 'bing.com',
            'duck duck go': 'duckduckgo.com'
        }
    
    def extract_explicit_urls(self, text: str) -> List[Dict]:
        """Extract explicitly mentioned URLs from text"""
        urls = []
        
        # Regex for URLs (simplified but effective)
        url_pattern = re.compile(
            r'(?:(?:https?://)?(?:www\.)?'
            r'(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
            r'(?:/[^\s]*)?)'
        )
        
        matches = url_pattern.findall(text)
        for match in matches:
            # Ensure it has a protocol
            if not match.startswith(('http://', 'https://')):
                match = 'https://' + match
            
            urls.append({
                'url': match,
                'type': 'explicit',
                'confidence': 'high',
                'original_text': match
            })
        
        return urls
    
    def might_be_url_description(self, text: str) -> bool:
        """Check if text might be describing a URL"""
        text_lower = text.lower()
        
        # Check for URL triggers
        for trigger in self.url_triggers:
            if trigger in text_lower:
                return True
        
        # Check for known site references
        for key in self.known_sites.keys():
            if key in text_lower:
                return True
        
        return False
    
    async def infer_url(self, text: str) -> Dict:
        """
        Infer URL from vague description
        Returns dict with url, confidence, explanation, and alternatives
        """
        text_lower = text.lower().strip()
        
        # First check for known sites
        for description, domain in self.known_sites.items():
            if description in text_lower:
                if isinstance(domain, list):
                    return {
                        'url': f'https://{domain[0]}',
                        'confidence': 'high',
                        'explanation': f'Recognized "{description}" reference',
                        'alternatives': [f'https://{d}' for d in domain[1:]],
                        'type': 'inferred'
                    }
                else:
                    return {
                        'url': f'https://{domain}',
                        'confidence': 'high',
                        'explanation': f'Recognized "{description}" as known site',
                        'alternatives': [],
                        'type': 'inferred'
                    }
        
        # Try to extract keywords and build domain
        keywords = self._extract_keywords_for_domain(text)
        if keywords:
            probable_url = self._build_url_from_keywords(keywords)
            return {
                'url': probable_url,
                'confidence': 'medium',
                'explanation': f'Built from keywords: {", ".join(keywords)}',
                'alternatives': self._generate_alternatives(probable_url),
                'type': 'inferred'
            }
        
        # Last resort - look for partial domain patterns
        partial_domain = self._extract_partial_domain(text)
        if partial_domain:
            return {
                'url': f'https://{partial_domain}',
                'confidence': 'low',
                'explanation': 'Extracted partial domain pattern',
                'alternatives': self._generate_alternatives(f'https://{partial_domain}'),
                'type': 'inferred'
            }
        
        return {
            'url': '',
            'confidence': 'none',
            'explanation': 'Could not infer URL from description',
            'alternatives': [],
            'type': 'failed'
        }
    
    def _extract_keywords_for_domain(self, text: str) -> List[str]:
        """Extract keywords that might form a domain name"""
        # Remove common filler words
        stop_words = {
            'the', 'that', 'where', 'with', 'site', 'website',
            'webpage', 'online', 'place', 'thing', 'one'
        }
        
        # Extract meaningful words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Prioritize nouns and descriptive words
        return keywords[:3]  # Limit to avoid overly long domains
    
    def _build_url_from_keywords(self, keywords: List[str]) -> str:
        """Build a probable URL from keywords"""
        if not keywords:
            return ''
        
        # Try different combinations
        if len(keywords) == 1:
            domain = keywords[0]
        elif len(keywords) == 2:
            # Try both concatenated and hyphenated
            domain = ''.join(keywords)
        else:
            # Use first two most relevant
            domain = ''.join(keywords[:2])
        
        return f'https://{domain}.com'
    
    def _extract_partial_domain(self, text: str) -> Optional[str]:
        """Try to extract partial domain patterns"""
        # Look for word.word patterns
        pattern = re.search(r'\b([a-zA-Z]+)\.([a-zA-Z]{2,})\b', text)
        if pattern:
            return pattern.group(0)
        
        # Look for domain-like words
        words = text.split()
        for word in words:
            if len(word) > 4 and word.isalpha():
                return f'{word}.com'
        
        return None
    
    def _generate_alternatives(self, base_url: str) -> List[str]:
        """Generate URL variations"""
        alternatives = []
        
        try:
            parsed = urlparse(base_url)
            domain = parsed.netloc or parsed.path
            
            # Remove www if present
            domain = domain.replace('www.', '')
            
            # Extract base name
            parts = domain.split('.')
            if len(parts) >= 2:
                base_name = parts[0]
                
                # Try different TLDs
                for tld in ['.com', '.org', '.net', '.io', '.co']:
                    alt_url = f'https://{base_name}{tld}'
                    if alt_url != base_url:
                        alternatives.append(alt_url)
                
                # Try with hyphens if camelCase or concatenated
                if len(base_name) > 8 and '-' not in base_name:
                    # Simple word boundary detection
                    hyphenated = self._add_hyphens(base_name)
                    if hyphenated != base_name:
                        alternatives.append(f'https://{hyphenated}.com')
        except:
            pass
        
        return alternatives[:4]  # Limit alternatives
    
    def _add_hyphens(self, domain: str) -> str:
        """Add hyphens at word boundaries"""
        # Simple heuristic - add hyphen before capital letters
        result = re.sub(r'(?<!^)(?=[A-Z])', '-', domain)
        
        # Or try to split at common word boundaries
        if result == domain:
            # Look for common word endings
            for i in range(3, len(domain) - 3):
                if domain[:i] in ['get', 'buy', 'find', 'best', 'my', 'the']:
                    result = domain[:i] + '-' + domain[i:]
                    break
        
        return result.lower()
    
    async def validate_url(self, url: str) -> bool:
        """Quick validation to check if URL is reachable"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=5, allow_redirects=True) as response:
                    return response.status < 400
        except:
            return False
