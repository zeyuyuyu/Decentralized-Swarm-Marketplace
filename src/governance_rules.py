from typing import Dict, List, Any, Callable
from dataclasses import dataclass
import json
import logging

@dataclass
class Rule:
    name: str
    condition: Callable
    action: Callable
    priority: int
    metadata: Dict[str, Any]

class GovernanceEngine:
    def __init__(self):
        self.rules: List[Rule] = []
        self.logger = logging.getLogger(__name__)

    def add_rule(self, rule: Rule) -> None:
        """Add a new governance rule to the engine."""
        self.rules.append(rule)
        self.rules.sort(key=lambda x: x.priority, reverse=True)

    def evaluate_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate all rules against the given context."""
        results = []
        for rule in self.rules:
            try:
                if rule.condition(context):
                    action_result = rule.action(context)
                    results.append({
                        'rule': rule.name,
                        'status': 'executed',
                        'result': action_result
                    })
                else:
                    results.append({
                        'rule': rule.name,
                        'status': 'skipped',
                        'result': None
                    })
            except Exception as e:
                self.logger.error(f'Error executing rule {rule.name}: {str(e)}')
                results.append({
                    'rule': rule.name,
                    'status': 'error',
                    'error': str(e)
                })
        return results

    def export_rules(self, filepath: str) -> None:
        """Export all rules to a JSON file."""
        rules_data = [{
            'name': rule.name,
            'priority': rule.priority,
            'metadata': rule.metadata
        } for rule in self.rules]
        
        with open(filepath, 'w') as f:
            json.dump(rules_data, f, indent=2)

    @staticmethod
    def create_default_rules() -> List[Rule]:
        """Create a set of default governance rules."""
        return [
            Rule(
                name='resource_limit_check',
                condition=lambda ctx: ctx.get('resource_usage', 0) > ctx.get('resource_limit', 100),
                action=lambda ctx: {'action': 'scale_down', 'reason': 'resource limit exceeded'},
                priority=100,
                metadata={'description': 'Checks if resource usage exceeds limits'}
            ),
            Rule(
                name='health_check',
                condition=lambda ctx: ctx.get('health_status') == 'degraded',
                action=lambda ctx: {'action': 'restart_service', 'reason': 'health check failed'},
                priority=90,
                metadata={'description': 'Monitors service health status'}
            ),
            Rule(
                name='performance_optimization',
                condition=lambda ctx: ctx.get('response_time', 0) > ctx.get('sla_threshold', 1000),
                action=lambda ctx: {'action': 'optimize_performance', 'reason': 'SLA breach'},
                priority=80,
                metadata={'description': 'Ensures performance meets SLA requirements'}
            )
        ]

    def load_rules_from_file(self, filepath: str) -> None:
        """Load rules from a JSON configuration file."""
        with open(filepath, 'r') as f:
            rules_data = json.load(f)
            
        for rule_data in rules_data:
            # Custom rule loading logic here
            # This would need to be implemented based on how rules are serialized
            pass

def create_governance_engine() -> GovernanceEngine:
    """Factory function to create and initialize a governance engine."""
    engine = GovernanceEngine()
    for rule in GovernanceEngine.create_default_rules():
        engine.add_rule(rule)
    return engine