#!/usr/bin/env python3
"""
BLACKREIGN - Advanced Web Vulnerability Scanner
Ethical security testing tool for white hat hackers and bug bounty hunters
"""

import asyncio
import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from core.engine import ScanEngine
from utils.logger import Logger
from utils.parser import URLParser

console = Console()

def display_banner():
    """Display BLACKREIGN ASCII banner"""
    banner = r"""
    ____  __           __   ____       _           
   / __ )/ /___ ______/ /__/ __ \___  (_)___ _____ 
  / __  / / __ `/ ___/ //_/ /_/ / _ \/ / __ `/ __ \
 / /_/ / / /_/ / /__/ ,< / _, _/  __/ / /_/ / / / /
/_____/_/\__,_/\___/_/|_/_/ |_|\___/_/\__, /_/ /_/  
                                     /____/         """
    
    console.print(Panel(banner, border_style="red", padding=(1, 2)))
    console.print("[red bold]⚔️  BLACKREIGN - Web Vulnerability Scanner  ⚔️[/red bold]")
    console.print("[dim]Ethical security testing tool for authorized use only[/dim]\n")

async def ethical_check(target: str) -> bool:
    """Ethical confirmation before scanning"""
    console.print(f"\n[yellow]⚠️  TARGET: {target}[/yellow]")
    console.print("[red]⚠️  LEGAL WARNING: Only scan targets you own or have explicit permission to test![/red]")
    
    response = console.input("\n[bold]Do you have permission to scan this target? (yes/no): [/bold]")
    
    if response.lower() != 'yes':
        console.print("[red]✗ Scan aborted. Remember: Always get permission before testing![/red]")
        return False
    
    console.print("[green]✓ Authorization confirmed. Starting scan...[/green]\n")
    return True

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='BLACKREIGN Web Vulnerability Scanner')
    parser.add_argument('-u', '--url', help='Single target URL')
    parser.add_argument('-l', '--list', help='File containing list of targets')
    parser.add_argument('--deep', action='store_true', help='Perform deep scanning with crawling')
    parser.add_argument('--stealth', action='store_true', help='Enable stealth mode (slower, random delays)')
    parser.add_argument('--light', action='store_true', help='Light scan (only critical vulnerabilities)')
    parser.add_argument('--output', help='Output file name (without extension)')
    
    args = parser.parse_args()
    
    # Display banner
    display_banner()
    
    # Determine targets
    targets = []
    if args.url:
        targets = [args.url]
    elif args.list:
        try:
            with open(args.list, 'r') as f:
                targets = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            console.print(f"[red]Error: File '{args.list}' not found[/red]")
            sys.exit(1)
    else:
        # Interactive mode
        console.print("[yellow]No target specified. Use -u or -l for scanning.[/yellow]")
        console.print("[dim]Example: python main.py -u https://example.com --deep[/dim]")
        sys.exit(0)
    
    # Validate URLs
    valid_targets = []
    for target in targets:
        if URLParser.is_valid_url(target):
            valid_targets.append(URLParser.normalize_url(target))
        else:
            console.print(f"[red]Invalid URL: {target}[/red]")
    
    if not valid_targets:
        console.print("[red]No valid targets to scan[/red]")
        sys.exit(1)
    
    # Scan each target
    all_results = []
    logger = Logger()
    
    for target in valid_targets:
        # Ethical check
        if not await ethical_check(target):
            continue
            
        # Initialize scan engine
        engine = ScanEngine(target, deep=args.deep, stealth=args.stealth, light=args.light)
        await engine.initialize()
        
        # Perform scan
        results = await engine.scan()
        all_results.extend(results)
        
        # Display results
        logger.display_results(results)
        
        # Save report if requested
        if args.output:
            output_name = f"{args.output}_{target.replace('https://', '').replace('http://', '').replace('/', '_')}"
            logger.save_report(results, output_name, 'json')
            logger.save_report(results, output_name, 'txt')
        
        await engine.close()
    
    # Summary
    vuln_count = len([r for r in all_results if r.get('type') not in ['recon']])
    console.print(f"\n[bold green]✓ Scan Complete![/bold green]")
    console.print(f"[cyan]Total Vulnerabilities Found: {vuln_count}[/cyan]")
    
    if vuln_count > 0:
        console.print("[yellow]⚠️  Review findings and remediate vulnerabilities[/yellow]")
    else:
        console.print("[green]No vulnerabilities detected. Good security posture![/green]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Scan interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)
