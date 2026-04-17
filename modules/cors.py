from core.scanner import BaseScanner
from typing import Dict, List, Optional
import asyncio

class CORSScanner(BaseScanner):
    """CORS misconfiguration scanner"""
    
    async def scan(self) -> List[Dict]:
        """Execute CORS scan"""
        # Test with different origins
        test_origins = [
            "https://evil.com",
            "https://attacker.com",
            "null",
            "*",
            f"https://{self.target.split('//')[1].split('/')[0]}.evil.com",
            "http://localhost",
            "http://localhost:8000"
        ]
        
        for origin in test_origins:
            result = await self.test_origin(origin)
            if result:
                self.add_result(
                    'CORS Misconfiguration',
                    'MEDIUM',
                    self.target,
                    f"Origin '{origin}' allowed with credentials"
                )
                
        return self.results
        
    async def test_origin(self, origin: str) -> Optional[Dict]:
        """Test CORS configuration for specific origin"""
        headers = {'Origin': origin}
        
        # Send request with custom origin
        response = await self.http_client.get(self.target, custom_headers=headers)
        
        if response:
            acao = response.headers.get('Access-Control-Allow-Origin', '')
            accc = response.headers.get('Access-Control-Allow-Credentials', '')
            
            # Check if origin is reflected or wildcard with credentials
            if acao == origin or (acao == '*' and accc.lower() == 'true'):
                return {
                    'vulnerable': True,
                    'origin': origin,
                    'acao': acao,
                    'accc': accc
                }
                
        return None
