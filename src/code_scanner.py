import re
from typing import Dict, List, Optional
from pathlib import Path

class ContractScanner:
    def __init__(self):
        self.vulnerability_patterns = {
            'reentrancy': r'(call\.value|transfer|send)\(',
            'integer_overflow': r'\+\+|\+=|\-\-|\-=',
            'unchecked_external_call': r'\.call\(',
            'tx_origin': r'tx\.origin',
            'timestamp_dependence': r'block\.timestamp|now'
        }
        
        self.severity_levels = {
            'reentrancy': 'CRITICAL',
            'integer_overflow': 'HIGH',
            'unchecked_external_call': 'HIGH',
            'tx_origin': 'MEDIUM',
            'timestamp_dependence': 'LOW'
        }

    def scan_contract(self, contract_path: Path) -> Dict:
        """
        Scans a smart contract file for common security vulnerabilities
        Returns dict with findings and severity levels
        """
        if not contract_path.exists():
            raise FileNotFoundError(f'Contract file not found: {contract_path}')

        with open(contract_path, 'r') as f:
            content = f.read()

        findings = {}
        
        for vuln_type, pattern in self.vulnerability_patterns.items():
            matches = re.finditer(pattern, content)
            locations = []
            
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                locations.append({
                    'line': line_no,
                    'snippet': content.split('\n')[line_no-1].strip()
                })
                
            if locations:
                findings[vuln_type] = {
                    'severity': self.severity_levels[vuln_type],
                    'locations': locations
                }

        return {
            'contract': contract_path.name,
            'findings': findings,
            'total_issues': sum(len(v['locations']) for v in findings.values())
        }

    def generate_report(self, scan_results: Dict) -> str:
        """
        Generates a formatted report from scan results
        """
        report = []
        report.append(f'Security Scan Report for {scan_results["contract"]}')
        report.append('=' * 50)
        
        if scan_results['total_issues'] == 0:
            report.append('No security issues found.')
            return '\n'.join(report)
            
        report.append(f'Total Issues Found: {scan_results["total_issues"]}\n')
        
        for vuln_type, details in scan_results['findings'].items():
            report.append(f'{vuln_type.upper()} - Severity: {details["severity"]}')
            
            for loc in details['locations']:
                report.append(f'  Line {loc["line"]}: {loc["snippet"]}')
            report.append('')
            
        return '\n'.join(report)

    def batch_scan(self, directory: Path) -> List[Dict]:
        """
        Scans all smart contracts in a directory
        """
        results = []
        for contract_file in directory.glob('*.sol'):
            try:
                scan_result = self.scan_contract(contract_file)
                results.append(scan_result)
            except Exception as e:
                print(f'Error scanning {contract_file}: {str(e)}')
        return results

def main():
    scanner = ContractScanner()
    
    # Example usage
    contract_dir = Path('./contracts')
    if contract_dir.exists():
        results = scanner.batch_scan(contract_dir)
        for result in results:
            print(scanner.generate_report(result))
            print('\n' + '-'*50 + '\n')

if __name__ == '__main__':
    main()