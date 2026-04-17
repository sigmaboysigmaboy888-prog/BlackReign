# BLACKREIGN - Advanced Web Vulnerability Scanner

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)](https://www.python.org/)

## ⚠️ DISCLAIMER

**BLACKREIGN is designed for ethical security testing and educational purposes only.**

- Only scan websites you own or have explicit written permission to test
- Unauthorized scanning may be illegal in your jurisdiction
- The authors assume no liability for misuse of this tool
- Always comply with responsible disclosure practices

## 🎯 Features

- **Multi-threaded Async Scanning** - Fast and efficient vulnerability detection
- **Real Detection Logic** - Actual vulnerability confirmation, not just guesswork
- **Multiple Vulnerability Types:**
  - SQL Injection (Error-based)
  - Cross-Site Scripting (Reflected)
  - Local File Inclusion
  - Open Redirect
  - CORS Misconfigurations

- **Reconnaissance Engine**:
  - Header analysis
  - Form extraction
  - Link crawling
  - Parameter discovery

- **Advanced Features**:
  - Stealth mode with random delays
  - Deep crawling mode
  - Light scan option
  - Rate limiting
  - WAF awareness

- **Professional Output**:
  - Colored CLI interface
  - JSON/TXT report generation
  - Severity classification (HIGH/MEDIUM/LOW)

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/blackreign/scanner.git
cd blackreign

# Install dependencies
pip install -r requirements.txt

# Verify installation
python main.py --help
