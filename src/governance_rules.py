# Governance Rules Implementation
from dataclasses import dataclass
from typing import Dict, List
import math

@dataclass
class ParticipantStats:
    reputation_score: float
    successful_transactions: int
    total_stake: float
    last_active: int  # Unix timestamp

class GovernanceSystem:
    def __init__(self):
        self.participants: Dict[str, ParticipantStats] = {}
        self.proposals: List[dict] = []
        self.min_reputation_to_propose = 100
        self.proposal_stake_requirement = 50.0
    
    def calculate_voting_power(self, participant_id: str) -> float:
        if participant_id not in self.participants:
            return 0.0
            
        stats = self.participants[participant_id]
        
        # Voting power formula incorporating multiple factors
        base_power = stats.reputation_score * math.log(1 + stats.successful_transactions)
        stake_multiplier = math.sqrt(1 + stats.total_stake)
        activity_decay = max(0.1, (stats.last_active - 604800) / stats.last_active)  # 7-day decay
        
        return base_power * stake_multiplier * activity_decay
    
    def submit_proposal(self, participant_id: str, proposal_data: dict) -> bool:
        if participant_id not in self.participants:
            return False
            
        participant = self.participants[participant_id]
        
        if (participant.reputation_score < self.min_reputation_to_propose or
            participant.total_stake < self.proposal_stake_requirement):
            return False
            
        self.proposals.append({
            'id': len(self.proposals) + 1,
            'proposer': participant_id,
            'data': proposal_data,
            'votes_for': 0.0,
            'votes_against': 0.0,
            'voters': set()
        })
        return True
    
    def cast_vote(self, participant_id: str, proposal_id: int, support: bool) -> bool:
        if proposal_id > len(self.proposals) or participant_id not in self.participants:
            return False
            
        proposal = self.proposals[proposal_id - 1]
        if participant_id in proposal['voters']:
            return False
            
        voting_power = self.calculate_voting_power(participant_id)
        if support:
            proposal['votes_for'] += voting_power
        else:
            proposal['votes_against'] += voting_power
            
        proposal['voters'].add(participant_id)
        return True
    
    def update_reputation(self, participant_id: str, delta: float):
        if participant_id not in self.participants:
            self.participants[participant_id] = ParticipantStats(
                reputation_score=0.0,
                successful_transactions=0,
                total_stake=0.0,
                last_active=0
            )
        
        self.participants[participant_id].reputation_score = max(
            0.0,
            self.participants[participant_id].reputation_score + delta
        )
    
    def get_proposal_status(self, proposal_id: int) -> dict:
        if proposal_id > len(self.proposals):
            return {'error': 'Invalid proposal ID'}
            
        proposal = self.proposals[proposal_id - 1]
        total_votes = proposal['votes_for'] + proposal['votes_against']
        
        return {
            'id': proposal_id,
            'total_votes': total_votes,
            'approval_ratio': proposal['votes_for'] / total_votes if total_votes > 0 else 0,
            'status': 'active' if total_votes < 1000 else 'completed'
        }