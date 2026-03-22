import os
import subprocess
import json

class CodeScanner:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def scan_code(self):
        """Performs advanced code scanning and vulnerability detection."""
        # Run static code analysis tools
        self.run_code_linter()
        self.run_dependency_checker()
        self.run_security_scanner()

        # Aggregate and format results
        results = {
            "linter_issues": self.linter_issues,
            "dependency_vulnerabilities": self.dependency_vulnerabilities,
            "security_findings": self.security_findings
        }

        return results

    def run_code_linter(self):
        """Runs a code linter and stores the issues."""
        linter_cmd = ["pylint", self.repo_path]
        linter_output = subprocess.check_output(linter_cmd)
        self.linter_issues = json.loads(linter_output)

    def run_dependency_checker(self):
        """Checks project dependencies for known vulnerabilities."""
        dep_checker_cmd = ["safety", "check", "--json"]
        dep_checker_output = subprocess.check_output(dep_checker_cmd)
        self.dependency_vulnerabilities = json.loads(dep_checker_output)

    def run_security_scanner(self):
        """Scans the codebase for security vulnerabilities."""
        security_scanner_cmd = ["bandit", "-r", self.repo_path, "-f", "json"]
        security_scanner_output = subprocess.check_output(security_scanner_cmd)
        self.security_findings = json.loads(security_scanner_output)
