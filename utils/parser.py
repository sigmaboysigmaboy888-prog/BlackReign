from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Optional
import re

class URLParser:
    """URL parsing utilities"""
    
    @staticmethod
    def extract_params(url: str) -> Dict[str, List[str]]:
        """Extract parameters from URL"""
        parsed = urlparse(url)
        return parse_qs(parsed.query)
        
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format"""
        pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(pattern, url) is not None
        
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL format"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')
