import os
import json

class GovernanceRules:
    def __init__(self, config_file='governance_config.json'):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                'min_stake': 1000,
                'voting_period': 604800,  # 1 week in seconds
                'approval_threshold': 0.6
            }
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def validate_proposal(self, proposal):
        # Check if proposal meets governance requirements
        if proposal['stake'] < self.config['min_stake']:
            return False
        if proposal['voting_period'] < self.config['voting_period']:
            return False
        return True

    def tally_votes(self, proposal):
        # Tally votes and check if proposal is approved
        total_votes = sum(proposal['votes'].values())
        approve_votes = sum(vote for vote in proposal['votes'].values() if vote)
        return approve_votes / total_votes >= self.config['approval_threshold']
