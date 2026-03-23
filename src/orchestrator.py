import multiprocessing as mp
import subprocess
import json
import time

class Orchestrator:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.processes = []

    def start_nodes(self):
        for node_config in self.config['nodes']:
            p = mp.Process(target=self.run_node, args=(node_config,))
            p.start()
            self.processes.append(p)

    def run_node(self, node_config):
        cmd = ['python', 'src/main.py', '--node-id', node_config['id']]
        subprocess.run(cmd, check=True)

    def stop_nodes(self):
        for p in self.processes:
            p.terminate()
        for p in self.processes:
            p.join()

    def run_secure_computation(self):
        pool = mp.Pool(processes=len(self.config['nodes']))
        results = pool.map(self.run_secure_computation_node, self.config['nodes'])
        pool.close()
        pool.join()
        return self.aggregate_results(results)

    def run_secure_computation_node(self, node_config):
        cmd = ['python', 'src/secure_computation.py', '--node-id', node_config['id']]
        result = subprocess.run(cmd, capture_output=True, check=True)
        return json.loads(result.stdout)

    def aggregate_results(self, results):
        aggregated = {}
        for result in results:
            for key, value in result.items():
                if key not in aggregated:
                    aggregated[key] = []
                aggregated[key].append(value)
        return aggregated

if __name__ == '__main__':
    orchestrator = Orchestrator('config.json')
    orchestrator.start_nodes()
    time.sleep(60)  # Let nodes run for a while
    result = orchestrator.run_secure_computation()
    print(result)
    orchestrator.stop_nodes()