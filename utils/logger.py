from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
from typing import List, Dict
import json
import os

class Logger:
    """Enhanced logging with rich formatting"""
    
    def __init__(self):
        self.console = Console()
        self.scan_start = datetime.now()
        
    def info(self, message: str):
        """Log info message"""
        self.console.print(f"\033[96m➜\033[0m {message}")
        
    def success(self, message: str):
        """Log success message"""
        self.console.print(f"\033[92m✓\033[0m {message}")
        
    def warning(self, message: str):
        """Log warning message"""
        self.console.print(f"\033[93m⚠\033[0m {message}")
        
    def error(self, message: str):
        """Log error message"""
        self.console.print(f"\033[91m✗\033[0m {message}")
        
    def vulnerability(self, vuln_type: str, severity: str, url: str, details: str):
        """Log vulnerability found"""
        severity_colors = {
            'HIGH': '91',
            'MEDIUM': '93',
            'LOW': '94'
        }
        color = severity_colors.get(severity, '97')
        
        self.console.print(f"\n\033[{color}m🔥 {vuln_type}\033[0m")
        self.console.print(f"  Severity: \033[{color}m{severity}\033[0m")
        self.console.print(f"  URL: {url}")
        self.console.print(f"  Details: {details}")
        
    def display_results(self, results: List[Dict]):
        """Display scan results in table format"""
        vuln_results = [r for r in results if r.get('type') != 'recon']
        
        if not vuln_results:
            self.info("No vulnerabilities found")
            return
            
        self.console.print("\n\033[95m┌─────────────────────────────────────────────────┐\033[0m")
        self.console.print("\033[95m│                 SCAN RESULTS                     │\033[0m")
        self.console.print("\033[95m└─────────────────────────────────────────────────┘\033[0m\n")
        
        for result in vuln_results:
            self.vulnerability(
                result.get('type', 'Unknown'),
                result.get('severity', 'N/A'),
                result.get('url', 'N/A'),
                result.get('details', 'N/A')
            )
        
    def save_report(self, results: List[Dict], filename: str, format: str = 'json'):
        """Save scan report"""
        try:
            os.makedirs('reports', exist_ok=True)
            filepath = os.path.join('reports', filename)
            
            report = {
                'scan_target': results[0].get('target') if results else 'Unknown',
                'scan_time': self.scan_start.isoformat(),
                'scan_duration': (datetime.now() - self.scan_start).total_seconds(),
                'vulnerabilities': [r for r in results if r.get('type') != 'recon'],
                'recon_data': [r for r in results if r.get('type') == 'recon']
            }
            
            if format == 'json':
                with open(f"{filepath}.json", 'w') as f:
                    json.dump(report, f, indent=2)
                self.success(f"Report saved to {filepath}.json")
            elif format == 'txt':
                with open(f"{filepath}.txt", 'w') as f:
                    f.write(f"BLACKREIGN Scan Report\n")
                    f.write(f"=====================\n\n")
                    f.write(f"Target: {report['scan_target']}\n")
                    f.write(f"Scan Time: {report['scan_time']}\n")
                    f.write(f"Duration: {report['scan_duration']:.2f} seconds\n\n")
                    f.write(f"Vulnerabilities Found: {len(report['vulnerabilities'])}\n\n")
                    
                    for vuln in report['vulnerabilities']:
                        f.write(f"[{vuln['severity']}] {vuln['type']}\n")
                        f.write(f"  URL: {vuln['url']}\n")
                        f.write(f"  Details: {vuln['details']}\n\n")
                    
                self.success(f"Report saved to {filepath}.txt")
        except Exception as e:
            self.error(f"Failed to save report: {str(e)}")
