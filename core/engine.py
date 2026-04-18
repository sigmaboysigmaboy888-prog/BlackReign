import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import random
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import Logger
from utils.http import HTTPClient

class ScanEngine:
    """Main scanning engine with async capabilities"""
    
    def __init__(self, target: str, deep: bool = False, stealth: bool = False, light: bool = False, massive: bool = False):
        self.target = target.rstrip('/')
        self.deep = deep
        self.stealth = stealth
        self.light = light
        self.massive = massive
        self.logger = Logger()
        self.session = None
        self.results = []
        self.rate_limit = 1.5 if stealth else 0.3
        self.max_depth = 3 if deep else 1
        
    async def initialize(self):
        """Initialize HTTP session"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        headers = {'User-Agent': random.choice(user_agents)} if self.stealth else {}
        connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300)
        self.session = aiohttp.ClientSession(headers=headers, connector=connector)
        
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            
    async def scan(self) -> List[Dict]:
        """Execute full scan"""
        self.logger.info(f"Starting scan on {self.target}")
        
        if not self.light:
            await self.reconnaissance()
        
        await self.vulnerability_scan()
        
        return self.results
        
    async def reconnaissance(self):
        """Perform reconnaissance on target"""
        self.logger.info("Performing reconnaissance...")
        http_client = HTTPClient(self.session)
        
        try:
            response = await http_client.get(self.target)
            if response:
                self.results.append({
                    'type': 'recon',
                    'data': {
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'server': response.headers.get('Server', 'Unknown')
                    }
                })
                self.logger.success(f"Server: {response.headers.get('Server', 'Unknown')}")
        except Exception as e:
            self.logger.error(f"Recon error: {str(e)}")
            
    async def vulnerability_scan(self):
        """Scan for vulnerabilities"""
        self.logger.info("Starting vulnerability scan...")
        
        try:
            from modules.sqli import SQLiScanner
            from modules.xss import XSSScanner
            from modules.lfi import LFIScanner
            from modules.redirect import RedirectScanner
            from modules.cors import CORSScanner
            
            scanners = [
                SQLiScanner(self.session, self.target, self.stealth, self.massive),
                XSSScanner(self.session, self.target, self.stealth, self.massive),
                LFIScanner(self.session, self.target, self.stealth, self.massive),
                RedirectScanner(self.session, self.target, self.stealth),
                CORSScanner(self.session, self.target, self.stealth)
            ]
            
            for scanner in scanners:
                if not self.light or scanner.__class__.__name__ in ['SQLiScanner', 'XSSScanner']:
                    self.logger.info(f"Testing for {scanner.__class__.__name__.replace('Scanner', '')}...")
                    results = await scanner.scan()
                    self.results.extend(results)
                    await asyncio.sleep(self.rate_limit)
        except Exception as e:
            self.logger.error(f"Error in vulnerability scan: {str(e)}")
