from typing import Dict, Any, List, Optional
import asyncio
from abc import ABC, abstractmethod
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.http import HTTPClient
from core.validator import VulnerabilityValidator

class BaseScanner(ABC):
    """Base scanner class for all vulnerability modules"""
    
    def __init__(self, session, target: str, stealth: bool = False):
        self.session = session
        self.target = target
        self.stealth = stealth
        self.http_client = HTTPClient(session)
        self.validator = VulnerabilityValidator()
        self.results = []
        
    @abstractmethod
    async def scan(self) -> List[Dict]:
        """Execute vulnerability scan"""
        pass
        
    @abstractmethod
    async def test_payload(self, payload: str, location: str) -> Optional[Dict]:
        """Test a specific payload"""
        pass
        
    def add_result(self, vulnerability_type: str, severity: str, url: str, details: str):
        """Add vulnerability result"""
        self.results.append({
            'type': vulnerability_type,
            'severity': severity,
            'url': url,
            'details': details,
            'timestamp': asyncio.get_event_loop().time()
        })
