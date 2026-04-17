from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime
from typing import List, Dict
import json

class Logger:
    """Enhanced logging with rich formatting"""
    
    def __init__(self):
        self.console = Console()
        self.scan_start = datetime.now()
        
    def info(self, message: str):
        """Log info message"""
        self.console.print(f"[cyan]➜[/cyan] {message}")
        
    def success(self, message: str):
        """Log success message"""
        self.console.print(f"[green]✓[/green] {message}")
        
    def warning(self, message: str):
        """Log warning message"""
        self.console.print(f"[yellow]⚠[/yellow] {message}")
        
    def error(self, message: str):
        """Log error message"""
        self.console.print(f"[red]✗[/red] {message}")
        
    def vulnerability(self, vuln_type: str, severity: str, url: str, details: str):
        """Log vulnerability found"""
        severity_colors = {
            'HIGH': 'red',
            'MEDIUM': 'yellow',
            'LOW': 'blue'
        }
        color = severity_colors.get(severity, 'white')
        
        self.console.print(f"\n[{color}]🔥 {vuln_type}[/{color}]")
        self.console.print(f"  Severity: [{color}]{severity}[/{color}]")
        self.console.print(f"  URL: {url}")
        self.console.print(f"  Details: {details}")
        
    def display_results(self, results: List[Dict]):
        """Display scan results in table format"""
        if not results:
            self.info("No vulnerabilities found")
            return
            
        table = Table(title="Scan Results", style="bold")
        table.add_column("Type", style="cyan")
        table.add_column("Severity", style="red")
        table.add_column("URL", style="white")
        table.add_column("Details", style="dim")
        
        for result in results:
            if 'type' in result and result['type'] != 'recon':
                table.add_row(
                    result.get('type', 'Unknown'),
                    result.get('severity', 'N/A'),
                    result.get('url', 'N/A'),
                    result.get('details', 'N/A')[:50] + "..."
                )
                
        self.console.print(table)
        
    def save_report(self, results: List[Dict], filename: str, format: str = 'json'):
        """Save scan report"""
        report = {
            'scan_target': results[0].get('target') if results else 'Unknown',
            'scan_time': self.scan_start.isoformat(),
            'scan_duration': (datetime.now() - self.scan_start).total_seconds(),
            'vulnerabilities': [r for r in results if r.get('type') != 'recon'],
            'recon_data': [r for r in results if r.get('type') == 'recon']
        }
        
        if format == 'json':
            with open(f"{filename}.json", 'w') as f:
                json.dump(report, f, indent=2)
            self.success(f"Report saved to {filename}.json")
        elif format == 'txt':
            with open(f"{filename}.txt", 'w') as f:
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
                    
            self.success(f"Report saved to {filename}.txt")
