from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Set, Dict
import re

class ReconEngine:
    """Reconnaissance engine for information gathering"""
    
    def __init__(self, session, target: str):
        self.session = session
        self.target = target
        self.visited_urls: Set[str] = set()
        self.forms: List[Dict] = []
        self.links: Set[str] = set()
        self.parameters: Set[str] = set()
        
    async def analyze_response(self, url: str, html: str) -> Dict:
        """Analyze HTML response for recon data"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract forms
        forms = self._extract_forms(soup, url)
        
        # Extract links
        links = self._extract_links(soup, url)
        
        # Extract parameters
        params = self._extract_parameters(html)
        
        # Extract JavaScript files
        js_files = self._extract_js_files(soup, url)
        
        # Extract comments
        comments = self._extract_comments(html)
        
        return {
            'forms': forms,
            'links': links,
            'parameters': params,
            'js_files': js_files,
            'comments': comments
        }
        
    def _extract_forms(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract and analyze forms"""
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': urljoin(base_url, form.get('action', '')),
                'method': form.get('method', 'get').upper(),
                'inputs': []
            }
            
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                input_data = {
                    'name': input_tag.get('name', ''),
                    'type': input_tag.get('type', 'text'),
                    'value': input_tag.get('value', '')
                }
                form_data['inputs'].append(input_data)
                
            forms.append(form_data)
            self.forms.append(form_data)
            
        return forms
        
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from page"""
        links = []
        for link in soup.find_all(['a', 'link']):
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                if self._is_same_domain(full_url):
                    links.append(full_url)
                    self.links.add(full_url)
                    
        return links
        
    def _extract_parameters(self, html: str) -> List[str]:
        """Extract potential parameters from HTML"""
        param_pattern = r'(?:name|id|param|parameter)=["\']([^"\']+)["\']'
        params = re.findall(param_pattern, html, re.IGNORECASE)
        
        # Also check for URL parameters
        url_params = re.findall(r'[?&]([^=&]+)=', html)
        params.extend(url_params)
        
        unique_params = set(params)
        self.parameters.update(unique_params)
        
        return list(unique_params)
        
    def _extract_js_files(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract JavaScript files"""
        js_files = []
        for script in soup.find_all('script', src=True):
            js_url = urljoin(base_url, script['src'])
            js_files.append(js_url)
        return js_files
        
    def _extract_comments(self, html: str) -> List[str]:
        """Extract HTML comments"""
        comment_pattern = r'<!--(.*?)-->'
        comments = re.findall(comment_pattern, html, re.DOTALL)
        return [c.strip() for c in comments if c.strip()]
        
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to same domain"""
        parsed_url = urlparse(url)
        parsed_target = urlparse(self.target)
        return parsed_url.netloc == parsed_target.netloc or not parsed_url.netloc
