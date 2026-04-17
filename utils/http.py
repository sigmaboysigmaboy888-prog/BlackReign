import aiohttp
from typing import Optional, Dict, Any
import asyncio

class HTTPClient:
    """Async HTTP client wrapper"""
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.timeout = aiohttp.ClientTimeout(total=10)
        
    async def get(self, url: str, params: Optional[Dict] = None, 
                  custom_headers: Optional[Dict] = None, 
                  allow_redirects: bool = True) -> Optional[aiohttp.ClientResponse]:
        """Perform GET request"""
        try:
            headers = custom_headers or {}
            async with self.session.get(url, params=params, headers=headers, 
                                       timeout=self.timeout, 
                                       allow_redirects=allow_redirects) as response:
                # Read response body
                await response.read()
                return response
        except Exception as e:
            return None
            
    async def post(self, url: str, data: Optional[Dict] = None,
                   custom_headers: Optional[Dict] = None) -> Optional[aiohttp.ClientResponse]:
        """Perform POST request"""
        try:
            headers = custom_headers or {}
            async with self.session.post(url, data=data, headers=headers,
                                        timeout=self.timeout) as response:
                await response.read()
                return response
        except Exception as e:
            return None
