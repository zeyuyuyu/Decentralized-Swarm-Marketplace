import time
import random
from typing import Dict, List, Optional

class SwarmOrchestrator:
    def __init__(self):
        self.nodes: Dict[str, dict] = {}
        self.workload_history: Dict[str, List[float]] = {}
        self.health_checks: Dict[str, bool] = {}
        self.last_rebalance = time.time()

    def register_node(self, node_id: str, capacity: float, capabilities: List[str]) -> None:
        """Register a new node in the swarm"""
        self.nodes[node_id] = {
            'capacity': capacity,
            'current_load': 0.0,
            'capabilities': capabilities,
            'last_seen': time.time()
        }
        self.workload_history[node_id] = []
        self.health_checks[node_id] = True

    def update_node_status(self, node_id: str, current_load: float) -> None:
        """Update node status including load and health check"""
        if node_id in self.nodes:
            self.nodes[node_id]['current_load'] = current_load
            self.nodes[node_id]['last_seen'] = time.time()
            self.workload_history[node_id].append(current_load)
            
            # Keep last 10 measurements
            if len(self.workload_history[node_id]) > 10:
                self.workload_history[node_id].pop(0)

    def check_node_health(self, node_id: str) -> bool:
        """Perform health check on node"""
        if node_id not in self.nodes:
            return False

        # Check if node has reported in last 30 seconds
        if time.time() - self.nodes[node_id]['last_seen'] > 30:
            self.health_checks[node_id] = False
            return False

        # Check if average load is below 90% capacity
        recent_loads = self.workload_history.get(node_id, [])
        if recent_loads:
            avg_load = sum(recent_loads) / len(recent_loads)
            if avg_load > 0.9 * self.nodes[node_id]['capacity']:
                self.health_checks[node_id] = False
                return False

        self.health_checks[node_id] = True
        return True

    def get_optimal_node(self, required_capabilities: List[str]) -> Optional[str]:
        """Find the optimal node for a new workload based on capabilities and current load"""
        eligible_nodes = []
        
        for node_id, info in self.nodes.items():
            if not self.health_checks[node_id]:
                continue
                
            if all(cap in info['capabilities'] for cap in required_capabilities):
                # Calculate available capacity
                available = info['capacity'] - info['current_load']
                if available > 0:
                    eligible_nodes.append((node_id, available))

        if not eligible_nodes:
            return None

        # Sort by available capacity (descending)
        eligible_nodes.sort(key=lambda x: x[1], reverse=True)
        return eligible_nodes[0][0]

    def rebalance_workload(self) -> Dict[str, str]:
        """Rebalance workload across healthy nodes"""
        current_time = time.time()
        if current_time - self.last_rebalance < 60:  # Only rebalance every 60 seconds
            return {}

        self.last_rebalance = current_time
        migrations = {}

        # Find overloaded nodes
        overloaded = []
        underutilized = []

        for node_id, info in self.nodes.items():
            if not self.health_checks[node_id]:
                continue

            utilization = info['current_load'] / info['capacity']
            if utilization > 0.8:  # Over 80% utilized
                overloaded.append(node_id)
            elif utilization < 0.3:  # Under 30% utilized
                underutilized.append(node_id)

        # Calculate migrations
        for over_node in overloaded:
            if not underutilized:
                break

            excess_load = self.nodes[over_node]['current_load'] - \
                         (0.6 * self.nodes[over_node]['capacity'])  # Target 60% utilization

            for under_node in underutilized:
                available_capacity = self.nodes[under_node]['capacity'] - \
                                   self.nodes[under_node]['current_load']

                if available_capacity >= excess_load:
                    migrations[over_node] = under_node
                    break

        return migrations
