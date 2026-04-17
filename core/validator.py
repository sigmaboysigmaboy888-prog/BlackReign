from typing import Dict, Any, Optional
import re

class VulnerabilityValidator:
    """Validate and confirm vulnerabilities"""
    
    def __init__(self):
        self.sqli_patterns = [
            r"SQL syntax.*MySQL",
            r"Warning.*mysql_.*",
            r"MySQLSyntaxErrorException",
            r"valid MySQL result",
            r"PostgreSQL.*ERROR",
            r"Warning.*\Wpg_.*",
            r"valid PostgreSQL result",
            r"ORA-[0-9]{5}",
            r"Oracle error",
            r"SQLite/JDBCDriver",
            r"SQLite.Exception",
            r"System.Data.SQLite.SQLiteException",
            r"Warning.*sqlite_.*",
            r"valid SQLite",
            r"SQL Server.*Driver",
            r"Driver.*SQL Server",
            r"SQLServer JDBC Driver",
            r"com.microsoft.sqlserver",
            r"Unclosed quotation mark"
        ]
        
        self.xss_patterns = [
            r"<script.*?>.*?</script>",
            r"onload=.*?\(.*?\)",
            r"javascript:.*?\(.*?\)",
            r"<img.*?onerror=.*?>"
        ]
        
    def validate_sqli(self, original_response: str, test_response: str) -> bool:
        """Validate SQL injection vulnerability"""
        # Check for SQL errors in response
        for pattern in self.sqli_patterns:
            if re.search(pattern, test_response, re.IGNORECASE):
                return True
                
        # Check response difference
        if len(original_response) != len(test_response):
            diff_ratio = abs(len(original_response) - len(test_response)) / len(original_response)
            if diff_ratio > 0.3:  # Significant difference
                return True
                
        return False
        
    def validate_xss(self, original_response: str, test_response: str, payload: str) -> bool:
        """Validate XSS vulnerability"""
        # Check if payload is reflected without proper encoding
        if payload in test_response:
            # Check if it's not HTML encoded
            if '&lt;' not in payload or '&gt;' not in payload:
                return True
                
        # Check for XSS patterns
        for pattern in self.xss_patterns:
            if re.search(pattern, test_response, re.IGNORECASE):
                return True
                
        return False
        
    def validate_lfi(self, response: str, target_file: str) -> bool:
        """Validate LFI vulnerability"""
        lfi_indicators = [
            "root:x:0:0",
            "<?php",
            "define('DB_USER'",
            "SELECT * FROM",
            "Windows Registry Editor",
            "[boot loader]",
            "[fonts]",
            "autoeth0"
        ]
        
        for indicator in lfi_indicators:
            if indicator in response:
                return True
                
        return False
        
    def validate_redirect(self, original_location: str, new_location: str, target_domain: str) -> bool:
        """Validate open redirect vulnerability"""
        from urllib.parse import urlparse
        
        parsed_new = urlparse(new_location)
        parsed_target = urlparse(target_domain)
        
        # Check if redirects to different domain
        if parsed_new.netloc and parsed_new.netloc != parsed_target.netloc:
            return True
            
        return False
