import ast
import os
from radon.complexity import cc_visit
from radon.metrics import h_visit
from radon.raw import analyze
from typing import Dict, List, Any

class CodeQualityScanner:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.results: Dict[str, Any] = {}

    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single Python file for code quality metrics"""
        with open(file_path, 'r') as f:
            content = f.read()

        try:
            # Parse AST
            tree = ast.parse(content)
            
            # Calculate complexity metrics
            complexity_metrics = cc_visit(content)
            halstead_metrics = h_visit(content)
            raw_metrics = analyze(content)

            file_results = {
                'cyclomatic_complexity': [
                    {
                        'name': func.name,
                        'complexity': func.complexity,
                        'lineno': func.lineno
                    } for func in complexity_metrics
                ],
                'halstead_metrics': {
                    'h1': halstead_metrics.h1,
                    'h2': halstead_metrics.h2,
                    'N1': halstead_metrics.N1,
                    'N2': halstead_metrics.N2,
                    'vocabulary': halstead_metrics.vocabulary,
                    'length': halstead_metrics.length,
                    'volume': halstead_metrics.volume,
                    'difficulty': halstead_metrics.difficulty
                },
                'raw_metrics': {
                    'loc': raw_metrics.loc,
                    'lloc': raw_metrics.lloc,
                    'sloc': raw_metrics.sloc,
                    'comments': raw_metrics.comments,
                    'multi': raw_metrics.multi,
                    'blank': raw_metrics.blank
                },
                'ast_stats': {
                    'num_functions': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                    'num_classes': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                    'num_imports': len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])
                }
            }

            return file_results

        except Exception as e:
            return {'error': str(e)}

    def scan_repository(self) -> Dict[str, Any]:
        """Scan entire repository for code quality metrics"""
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.repo_path)
                    self.results[rel_path] = self.scan_file(file_path)

        return self.results

    def get_critical_issues(self) -> List[Dict[str, Any]]:
        """Identify critical code quality issues"""
        critical_issues = []

        for file_path, metrics in self.results.items():
            if 'error' in metrics:
                continue

            # Check for complex functions
            for func in metrics['cyclomatic_complexity']:
                if func['complexity'] > 10:
                    critical_issues.append({
                        'file': file_path,
                        'type': 'high_complexity',
                        'function': func['name'],
                        'complexity': func['complexity'],
                        'line': func['lineno']
                    })

            # Check for large files
            if metrics['raw_metrics']['lloc'] > 300:
                critical_issues.append({
                    'file': file_path,
                    'type': 'large_file',
                    'lloc': metrics['raw_metrics']['lloc']
                })

            # Check for low comment ratio
            if metrics['raw_metrics']['lloc'] > 0:
                comment_ratio = metrics['raw_metrics']['comments'] / metrics['raw_metrics']['lloc']
                if comment_ratio < 0.1:
                    critical_issues.append({
                        'file': file_path,
                        'type': 'low_comments',
                        'ratio': comment_ratio
                    })

        return critical_issues

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Generate repository-wide summary metrics"""
        total_lloc = 0
        total_complexity = 0
        num_functions = 0

        for metrics in self.results.values():
            if 'error' in metrics:
                continue

            total_lloc += metrics['raw_metrics']['lloc']
            total_complexity += sum(func['complexity'] for func in metrics['cyclomatic_complexity'])
            num_functions += metrics['ast_stats']['num_functions']

        return {
            'total_lloc': total_lloc,
            'avg_complexity': total_complexity / num_functions if num_functions > 0 else 0,
            'num_files': len(self.results),
            'num_functions': num_functions
        }
