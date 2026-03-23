import os
import json
import hashlib
from typing import List, Tuple
from .governance_rules import GovernanceRules

class DecentralizedSwarmMarketplace:
    def __init__(self):
        self.governance_rules = GovernanceRules()
        self.registered_users: List[str] = []
        self.proposals: List[Proposal] = []
        self.vote_registry: Dict[Tuple[str, int], bool] = {}

    def register_user(self, user_id: str):
        if user_id not in self.registered_users:
            self.registered_users.append(user_id)

    def submit_proposal(self, proposer_id: str, proposal_details: str) -> int:
        proposal = Proposal(proposer_id, proposal_details)
        self.proposals.append(proposal)
        return len(self.proposals) - 1

    def vote_on_proposal(self, voter_id: str, proposal_id: int, vote: bool):
        if voter_id in self.registered_users:
            self.vote_registry[(voter_id, proposal_id)] = vote

    def tally_votes(self, proposal_id: int) -> bool:
        yes_votes = 0
        no_votes = 0
        for (voter_id, pid), vote in self.vote_registry.items():
            if pid == proposal_id:
                if vote:
                    yes_votes += 1
                else:
                    no_votes += 1
        return yes_votes >= self.governance_rules.min_yes_votes and yes_votes > no_votes

class Proposal:
    def __init__(self, proposer_id: str, details: str):
        self.proposer_id = proposer_id
        self.details = details
        self.id = hashlib.sha256(f'{proposer_id}:{details}'.encode()).hexdigest()
