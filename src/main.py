import asyncio
import websockets
import json
import git
import os
from typing import Set, Dict

class GitSignalServer:
    def __init__(self):
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.repos: Dict[str, git.Repo] = {}
        
    async def register(self, websocket: websockets.WebSocketServerProtocol):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        finally:
            self.clients.remove(websocket)

    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        data = json.loads(message)
        if data['type'] == 'watch_repo':
            repo_path = data['repo_path']
            if repo_path not in self.repos:
                try:
                    repo = git.Repo(repo_path)
                    self.repos[repo_path] = repo
                    asyncio.create_task(self.monitor_repo(repo_path))
                    await websocket.send(json.dumps({
                        'type': 'success',
                        'message': f'Now watching {repo_path}'
                    }))
                except git.InvalidGitRepositoryError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': f'Invalid git repository: {repo_path}'
                    }))

    async def broadcast(self, message: dict):
        if self.clients:
            await asyncio.wait([
                client.send(json.dumps(message))
                for client in self.clients
            ])

    async def monitor_repo(self, repo_path: str):
        repo = self.repos[repo_path]
        last_commit = repo.head.commit
        
        while True:
            try:
                repo.remotes.origin.fetch()
                current_commit = repo.head.commit
                
                if current_commit != last_commit:
                    changes = {
                        'files_changed': list(current_commit.stats.files.keys()),
                        'insertions': current_commit.stats.total['insertions'],
                        'deletions': current_commit.stats.total['deletions'],
                        'message': current_commit.message,
                        'author': current_commit.author.name,
                        'hash': current_commit.hexsha
                    }
                    
                    await self.broadcast({
                        'type': 'repo_update',
                        'repo_path': repo_path,
                        'changes': changes
                    })
                    
                    last_commit = current_commit
                    
            except Exception as e:
                await self.broadcast({
                    'type': 'error',
                    'repo_path': repo_path,
                    'message': str(e)
                })
                
            await asyncio.sleep(10)

async def main():
    server = GitSignalServer()
    async with websockets.serve(server.register, 'localhost', 8765):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())