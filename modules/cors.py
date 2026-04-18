from core.scanner import BaseScanner
from typing import Dict, List, Optional
import asyncio

class CORSScanner(BaseScanner):
    """CORS misconfiguration scanner"""
    
    def __init__(self, session, target: str, stealth: bool = False):
        super().__init__(session, target, stealth, False)
        
    async def scan(self) -> List[Dict]:
        """Execute CORS scan"""
        test_origins = [
            "https://evil.com",
            "https://attacker.com",
            "null",
            "*",
            f"https://{self.target.split('//')[1].split('/')[0]}.evil.com",
            "http://localhost",
            "http://localhost:8000",
            "https://localhost",
            "http://127.0.0.1",
            "https://malicious.com"
        ]
        
        for origin in test_origins:
            result = await self._test_origin(origin)
            if result:
                self.add_result(
                    'CORS Misconfiguration',
                    'MEDIUM',
                    self.target,
                    f"Origin '{origin}' allowed with credentials"
                )
                
        return self.results
    
    async def _test_origin(self, origin: str) -> Optional[Dict]:
        """Test CORS configuration for specific origin"""
        try:
            headers = {'Origin': origin}
            response = await self.http_client.get(self.target, custom_headers=headers)
            
            if response:
                acao = response.headers.get('Access-Control-Allow-Origin', '')
                accc = response.headers.get('Access-Control-Allow-Credentials', '')
                
                if acao == origin or (acao == '*' and accc.lower() == 'true'):
                    return {'vulnerable': True, 'origin': origin, 'acao': acao, 'accc': accc}
        except Exception as e:
            pass
        return None
    
    async def test_payload(self, payload: str, location: str) -> Optional[Dict]:
        """Implement abstract method - CORS doesn't use traditional payloads"""
        return None
