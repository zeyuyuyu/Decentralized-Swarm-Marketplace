import os
import hashlib
import json
import requests

class CodeScanner:
    def __init__(self, swarm_endpoint):
        self.swarm_endpoint = swarm_endpoint

    def scan_directory(self, directory):
        """Recursively scan a directory for files and submit them to the swarm for analysis."""
        file_hashes = {}
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    file_hashes[file_path] = file_hash
                    self.submit_file_to_swarm(file_path, file_hash)
        return file_hashes

    def submit_file_to_swarm(self, file_path, file_hash):
        """Submit a file to the decentralized swarm for analysis."""
        data = {
            'file_path': file_path,
            'file_hash': file_hash
        }
        response = requests.post(self.swarm_endpoint + '/scan', json=data)
        if response.status_code == 200:
            print(f'Submitted {file_path} to the swarm for analysis.')
        else:
            print(f'Failed to submit {file_path} to the swarm. Error: {response.text}')
