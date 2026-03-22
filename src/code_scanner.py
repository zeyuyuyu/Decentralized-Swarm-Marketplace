import os
import sys
import re
import ast
import json
import hashlib
import requests

class CodeScanner:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.scan_results = {}
        self.vulnerability_db = self.load_vulnerability_db()

    def load_vulnerability_db(self):
        try:
            with open('vulnerability_db.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print('Vulnerability database not found. Fetching from remote...')
            response = requests.get('https://example.com/vulnerability_db.json')
            with open('vulnerability_db.json', 'w') as f:
                json.dump(response.json(), f)
            return response.json()

    def scan_file(self, file_path):
        with open(file_path, 'r') as f:
            code = f.read()
        ast_tree = ast.parse(code)
        self.scan_results[file_path] = self.analyze_ast(ast_tree)

    def analyze_ast(self, ast_tree):
        results = {}
        for node in ast.walk(ast_tree):
            for vuln in self.vulnerability_db:
                if vuln['pattern'] in ast.dump(node):
                    results[vuln['name']] = vuln['description']
        return results

    def scan_repo(self):
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.scan_file(file_path)
        return self.scan_results
