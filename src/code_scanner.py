import os
import ast
import hashlib

class CodeScanner:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def scan_codebase(self):
        """Recursively scan the codebase and return a report of potential issues."""
        report = {}
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            code = f.read()
                            report[file_path] = self.analyze_code(code)
                    except Exception as e:
                        report[file_path] = {'error': str(e)}
        return report

    def analyze_code(self, code):
        """Analyze the given code and return a report of potential issues."""
        report = {}
        try:
            tree = ast.parse(code)
            report['syntax_errors'] = self.check_syntax_errors(tree)
            report['code_complexity'] = self.calculate_code_complexity(tree)
            report['vulnerabilities'] = self.detect_vulnerabilities(code)
        except Exception as e:
            report['error'] = str(e)
        return report

    def check_syntax_errors(self, tree):
        """Check the AST for syntax errors."""
        return []

    def calculate_code_complexity(self, tree):
        """Calculate the complexity of the code based on the AST."""
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.Except)):
                complexity += 1
        return complexity

    def detect_vulnerabilities(self, code):
        """Detect potential vulnerabilities in the code."""
        vulnerabilities = []
        if 'eval(' in code:
            vulnerabilities.append('Potential code injection vulnerability')
        if 'subprocess.call(' in code:
            vulnerabilities.append('Potential command injection vulnerability')
        return vulnerabilities
