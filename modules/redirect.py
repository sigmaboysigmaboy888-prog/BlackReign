from core.scanner import BaseScanner
from typing import Dict, List, Optional
import asyncio
from urllib.parse import urlparse

class RedirectScanner(BaseScanner):
    """Open Redirect vulnerability scanner"""
    
    def __init__(self, session, target: str, stealth: bool = False):
        super().__init__(session, target, stealth, False)
        self.payloads = self._load_payloads()
        
    def _load_payloads(self) -> List[str]:
        """Load open redirect payloads"""
        return [
            "//evil.com",
            "https://evil.com",
            "http://evil.com",
            "///evil.com",
            "//evil.com/%2f..",
            "https://evil.com/%2f..",
            "//evil.com/..",
            "//evil.com?",
            "https://evil.com@google.com",
            "/\\\\evil.com",
            "\\\\evil.com",
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>"
        ]
        
    async def scan(self) -> List[Dict]:
        """Execute open redirect scan"""
        if '?' in self.target:
            await self._test_url_parameters()
        return self.results
        
    async def _test_url_parameters(self):
        """Test URL parameters for open redirect"""
        try:
            base_url, params = self.target.split('?', 1)
            param_pairs = [p.split('=', 1) for p in params.split('&')]
            
            for param_name, param_value in param_pairs:
                for payload in self.payloads:
                    test_params = {param_name: payload}
                    test_url = self._build_url(base_url, test_params)
                    
                    result = await self.test_payload(payload, test_url)
                    if result:
                        self.add_result(
                            'Open Redirect',
                            'MEDIUM',
                            test_url,
                            f"Parameter '{param_name}' vulnerable with payload: {payload}"
                        )
                        break
                        
                    await asyncio.sleep(0.2 if self.stealth else 0.05)
        except Exception as e:
            pass
            
    async def test_payload(self, payload: str, url: str) -> Optional[Dict]:
        """Test open redirect payload"""
        try:
            response = await self.http_client.get(url, allow_redirects=False)
            
            if response and response.status in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                if location:
                    parsed_new = urlparse(location)
                    parsed_target = urlparse(self.target)
                    
                    if parsed_new.netloc and parsed_new.netloc != parsed_target.netloc:
                        return {'vulnerable': True, 'payload': payload, 'redirect_to': location}
        except Exception as e:
            pass
        return None
        
    def _build_url(self, base_url: str, params: Dict) -> str:
        """Build URL with parameters"""
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
