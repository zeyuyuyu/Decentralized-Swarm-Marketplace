#!/usr/bin/env python3

import ast
import os
import git
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class CodeIssue:
    file: str
    line: int
    message: str
    severity: str

class CodeScanner:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.issues: List[CodeIssue] = []
        
    def scan_repo(self) -> List[CodeIssue]:
        """Scan entire repository for code quality issues"""
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    self.scan_file(filepath)
        return self.issues
    
    def scan_file(self, filepath: str) -> None:
        """Analyze a single Python file for issues"""
        with open(filepath, 'r') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
        except SyntaxError:
            self.issues.append(CodeIssue(
                file=filepath,
                line=1,
                message='Syntax error in file',
                severity='ERROR'
            ))
            return
            
        self._check_complexity(tree, filepath)
        self._check_naming(tree, filepath)
        self._check_imports(tree, filepath)
        
    def _check_complexity(self, tree: ast.AST, filepath: str) -> None:
        """Check for overly complex code structures"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 50:
                    self.issues.append(CodeIssue(
                        file=filepath,
                        line=node.lineno,
                        message=f'Function {node.name} is too long (>50 lines)',
                        severity='WARNING'
                    ))
                    
    def _check_naming(self, tree: ast.AST, filepath: str) -> None:
        """Check naming conventions"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name[0].isupper():
                    self.issues.append(CodeIssue(
                        file=filepath,
                        line=node.lineno,
                        message=f'Class {node.name} should use CapWords convention',
                        severity='INFO'
                    ))
                    
    def _check_imports(self, tree: ast.AST, filepath: str) -> None:
        """Check import statements"""
        imports: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for name in node.names:
                    if name.name in imports:
                        self.issues.append(CodeIssue(
                            file=filepath,
                            line=node.lineno,
                            message=f'Duplicate import of {name.name}',
                            severity='WARNING'
                        ))
                    imports.add(name.name)

def generate_report(issues: List[CodeIssue]) -> str:
    """Generate a markdown report from issues"""
    report = ["# Code Quality Report\n"]
    
    by_severity = {}
    for issue in issues:
        if issue.severity not in by_severity:
            by_severity[issue.severity] = []
        by_severity[issue.severity].append(issue)
        
    for severity in ['ERROR', 'WARNING', 'INFO']:
        if severity in by_severity:
            report.append(f"\n## {severity}s\n")
            for issue in by_severity[severity]:
                report.append(f"- {issue.file}:{issue.line} - {issue.message}\n")
                
    return ''.join(report)

def main():
    scanner = CodeScanner('.')
    issues = scanner.scan_repo()
    report = generate_report(issues)
    
    with open('code_quality_report.md', 'w') as f:
        f.write(report)
        
    print(f'Found {len(issues)} issues. See code_quality_report.md for details.')

if __name__ == '__main__':
    main()