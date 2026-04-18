#!/usr/bin/env python3
"""
BLACKREIGN - Advanced Web Vulnerability Scanner
Ethical security testing tool for white hat hackers and bug bounty hunters
"""

import asyncio
import sys
import argparse
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.engine import ScanEngine
from utils.logger import Logger
from utils.parser import URLParser

console = Console()

def display_banner():
    """Display BLACKREIGN ASCII banner"""
    banner = """
\033[90m    ____  __           __   ____       _           
   / __ )/ /___ ______/ /__/ __ \___  (_)___ _____ 
  / __  / / __ `/ ___/ //_/ /_/ / _ \/ / __ `/ __ \\
 / /_/ / / /_/ / /__/ ,< / _, _/  __/ / /_/ / / / /
/_____/_/\__,_/\___/_/|_/_/ |_|\___/_/\__, /_/ /_/  
                                     /____/\033[0m"""
    
    console.print(Panel(banner, border_style="red", padding=(1, 2)))
    console.print("\033[91m⚔️  BLACKREIGN - Web Vulnerability Scanner  ⚔️\033[0m")
    console.print("\033[90mEthical security testing tool for authorized use only\033[0m\n")

async def ethical_check(target: str) -> bool:
    """Ethical confirmation before scanning"""
    console.print(f"\n\033[93m⚠️  TARGET: {target}\033[0m")
    console.print("\033[91m⚠️  LEGAL WARNING: Only scan targets you own or have explicit permission to test!\033[0m")
    
    response = console.input("\n\033[1mDo you have permission to scan this target? (yes/no): \033[0m")
    
    if response.lower() != 'yes':
        console.print("\033[91m✗ Scan aborted. Remember: Always get permission before testing!\033[0m")
        return False
    
    console.print("\033[92m✓ Authorization confirmed. Starting scan...\033[0m\n")
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
    parser.add_argument('--massive', action='store_true', help='Use ultra massive payload collection')
    
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
            console.print(f"\033[91mError: File '{args.list}' not found\033[0m")
            sys.exit(1)
    else:
        console.print("\033[93mNo target specified. Use -u or -l for scanning.\033[0m")
        console.print("\033[90mExample: python main.py -u https://example.com --deep --massive\033[0m")
        sys.exit(0)
    
    # Validate URLs
    valid_targets = []
    for target in targets:
        if URLParser.is_valid_url(target):
            valid_targets.append(URLParser.normalize_url(target))
        else:
            console.print(f"\033[91mInvalid URL: {target}\033[0m")
    
    if not valid_targets:
        console.print("\033[91mNo valid targets to scan\033[0m")
        sys.exit(1)
    
    # Scan each target
    all_results = []
    logger = Logger()
    
    for target in valid_targets:
        # Ethical check
        if not await ethical_check(target):
            continue
            
        # Initialize scan engine
        engine = ScanEngine(target, deep=args.deep, stealth=args.stealth, light=args.light, massive=args.massive)
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
    console.print(f"\n\033[92m✓ Scan Complete!\033[0m")
    console.print(f"\033[96mTotal Vulnerabilities Found: {vuln_count}\033[0m")
    
    if vuln_count > 0:
        console.print("\033[93m⚠️  Review findings and remediate vulnerabilities\033[0m")
    else:
        console.print("\033[92mNo vulnerabilities detected. Good security posture!\033[0m")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\033[93m⚠️ Scan interrupted by user\033[0m")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n\033[91m✗ Error: {str(e)}\033[0m")
        sys.exit(1)
