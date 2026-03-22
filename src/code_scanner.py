import re
from typing import Dict, List, Optional

class SmartContractScanner:
    def __init__(self):
        self.vulnerability_patterns = {
            'reentrancy': r'(call\.value|send|transfer).*\(.*\)',
            'overflow': r'\+=|\-=|\*=|\/=',
            'timestamp_dependence': r'block\.timestamp|now',
            'unchecked_external_call': r'\.call\{.*\}\(\)',
            'tx_origin': r'tx\.origin'
        }
        
        self.severity_levels = {
            'reentrancy': 'CRITICAL',
            'overflow': 'HIGH',
            'timestamp_dependence': 'MEDIUM',
            'unchecked_external_call': 'HIGH',
            'tx_origin': 'MEDIUM'
        }

    def scan_contract(self, contract_code: str) -> List[Dict]:
        """
        Scan smart contract code for common vulnerabilities
        Returns list of found vulnerabilities with their details
        """
        findings = []
        
        for vuln_type, pattern in self.vulnerability_patterns.items():
            matches = re.finditer(pattern, contract_code)
            
            for match in matches:
                finding = {
                    'vulnerability_type': vuln_type,
                    'severity': self.severity_levels[vuln_type],
                    'line_number': contract_code.count('\n', 0, match.start()) + 1,
                    'code_snippet': self._get_context(contract_code, match.start()),
                    'description': self._get_vulnerability_description(vuln_type)
                }
                findings.append(finding)
        
        return findings

    def _get_context(self, code: str, pos: int, context_lines: int = 2) -> str:
        """Extract code context around the vulnerability"""
        lines = code.split('\n')
        line_no = code.count('\n', 0, pos)
        
        start = max(0, line_no - context_lines)
        end = min(len(lines), line_no + context_lines + 1)
        
        return '\n'.join(lines[start:end])

    def _get_vulnerability_description(self, vuln_type: str) -> str:
        descriptions = {
            'reentrancy': 'Potential reentrancy vulnerability detected. External calls could be re-entered before state updates.',
            'overflow': 'Possible arithmetic overflow/underflow. Consider using SafeMath.',
            'timestamp_dependence': 'Contract relies on block timestamp which can be manipulated by miners.',
            'unchecked_external_call': 'Unchecked external call could fail silently.',
            'tx_origin': 'Using tx.origin for authorization is dangerous.'
        }
        return descriptions.get(vuln_type, 'Unknown vulnerability type')

    def generate_report(self, findings: List[Dict]) -> str:
        """Generate a formatted security report from findings"""
        if not findings:
            return 'No vulnerabilities detected.'
            
        report = 'SMART CONTRACT SECURITY SCAN REPORT\n'
        report += '=' * 35 + '\n\n'
        
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM']:
            severity_findings = [f for f in findings if f['severity'] == severity]
            if severity_findings:
                report += f'{severity} Severity Issues:\n'
                report += '-' * 20 + '\n'
                
                for finding in severity_findings:
                    report += f"\nVulnerability: {finding['vulnerability_type']}\n"
                    report += f"Line Number: {finding['line_number']}\n"
                    report += f"Description: {finding['description']}\n"
                    report += f"Code Context:\n{finding['code_snippet']}\n"
                    report += '-' * 40 + '\n'
        
        return report

def scan_marketplace_contract(contract_path: str) -> Optional[str]:
    """
    Main function to scan a marketplace smart contract
    Returns a security report or None if file cannot be read
    """
    try:
        with open(contract_path, 'r') as f:
            contract_code = f.read()
            
        scanner = SmartContractScanner()
        findings = scanner.scan_contract(contract_code)
        return scanner.generate_report(findings)
        
    except FileNotFoundError:
        return None
    except Exception as e:
        return f'Error scanning contract: {str(e)}'