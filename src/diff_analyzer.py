import difflib
from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

class DiffAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.classifier = RandomForestClassifier(n_estimators=100)
        self.change_types = ['feature', 'bugfix', 'refactor', 'style', 'docs']
        
    def compute_diff(self, old_content: str, new_content: str) -> str:
        """Generate a unified diff between old and new content."""
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile='old',
            tofile='new'
        )
        return ''.join(diff)

    def extract_diff_features(self, diff_text: str) -> Dict[str, int]:
        """Extract numerical features from diff text."""
        features = {
            'lines_added': 0,
            'lines_removed': 0,
            'lines_modified': 0,
            'chunks': 0
        }
        
        for line in diff_text.split('\
'):
            if line.startswith('+') and not line.startswith('+++'):
                features['lines_added'] += 1
            elif line.startswith('-') and not line.startswith('---'):
                features['lines_removed'] += 1
            elif line.startswith('@@'):
                features['chunks'] += 1
                
        features['lines_modified'] = min(features['lines_added'], 
                                       features['lines_removed'])
        return features

    def train_classifier(self, diff_samples: List[str], labels: List[str]):
        """Train the semantic change classifier."""
        X = self.vectorizer.fit_transform(diff_samples)
        self.classifier.fit(X, labels)

    def classify_change(self, diff_text: str) -> str:
        """Classify the type of change in the diff."""
        X = self.vectorizer.transform([diff_text])
        prediction = self.classifier.predict(X)[0]
        return prediction

    def analyze(self, old_content: str, new_content: str) -> Dict:
        """Perform complete diff analysis including semantic classification."""
        diff_text = self.compute_diff(old_content, new_content)
        features = self.extract_diff_features(diff_text)
        
        try:
            change_type = self.classify_change(diff_text)
        except:
            change_type = 'unknown'
            
        analysis = {
            'diff': diff_text,
            'stats': features,
            'change_type': change_type,
            'impact_score': self._calculate_impact_score(features)
        }
        return analysis

    def _calculate_impact_score(self, features: Dict[str, int]) -> float:
        """Calculate an impact score based on diff features."""
        weights = {
            'lines_added': 0.4,
            'lines_removed': 0.4,
            'lines_modified': 0.1,
            'chunks': 0.1
        }
        
        score = sum(features[k] * weights[k] for k in weights)
        return min(10.0, score)  # Cap score at 10

    def get_risky_changes(self, diff_text: str) -> List[str]:
        """Identify potentially risky patterns in changes."""
        risky_patterns = [
            ('password', 'Potential security credential'),
            ('token', 'Potential security credential'),
            ('delete', 'Destructive operation'),
            ('drop', 'Destructive operation'),
            ('truncate', 'Destructive operation')
        ]
        
        risks = []
        for pattern, warning in risky_patterns:
            if pattern in diff_text.lower():
                risks.append(warning)
                
        return risks