"""
Intent Classifier
Classifies user intent from natural language queries
"""

import re
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Classifies user intent from natural language questions
    """
    
    # Intent patterns using keywords and phrases
    INTENT_PATTERNS = {
        'trend_analysis': [
            r'\btrend\b', r'\bover time\b', r'\bincreas(ing|e|ed)\b',
            r'\bdecreas(ing|e|ed)\b', r'\bgrow(th|ing)\b', r'\bdeclin(e|ing)\b',
            r'\bchanging\b', r'\bevolution\b', r'\btrajectory\b'
        ],
        'comparison': [
            r'\bcompare\b', r'\bvs\.?\b', r'\bversus\b', r'\bbetter\b',
            r'\bworse\b', r'\bdifference\b', r'\bhigher\b', r'\blower\b',
            r'\bbetween\b.*\band\b'
        ],
        'explanation': [
            r'\bwhy\b', r'\bhow\b', r'\bexplain\b', r'\breason\b',
            r'\bcause\b', r'\bwhat.*mean\b', r'\bwhat.*affect\b',
            r'\broot cause\b', r'\bdriv(e|ing|en)\b'
        ],
        'recommendation': [
            r'\brecommend\b', r'\bsugg(est|estion)\b', r'\bwhat should\b',
            r'\badvice\b', r'\baction\b', r'\bimprove\b', r'\boptimiz\w+\b',
            r'\benhance\b'
        ],
        'kpi_query': [
            r'\bkpi\b', r'\bmetric\b', r'\bindicator\b', r'\bperformance\b',
            r'\bscore\b', r'\brating\b', r'\bvalue of\b'
        ],
        'dashboard_summary': [
            r'\bdashboard\b', r'\boverview\b', r'\bsummary\b', r'\bsummariz\w+\b',
            r'\ball.*kpis\b', r'\bshow me everything\b'
        ],
        'anomaly_detection': [
            r'\banomal(y|ies)\b', r'\boutlier\b', r'\bunusual\b',
            r'\bstrange\b', r'\bodd\b', r'\bunexpected\b', r'\birregular\b'
        ],
        'general_query': [
            r'\bwhat is\b', r'\btell me about\b', r'\bshow me\b',
            r'\bgive me\b', r'\bfind\b', r'\blist\b'
        ]
    }
    
    def classify_intent(self, query: str) -> Tuple[str, float]:
        """
        Classify the intent of a user query
        
        Args:
            query: User's natural language query
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        query_lower = query.lower()
        
        intent_scores = {}
        
        # Calculate score for each intent
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    matches += 1
                    score += 1
            
            if matches > 0:
                # Normalize by number of patterns
                intent_scores[intent] = score / len(patterns)
        
        # If no matches, default to general_query
        if not intent_scores:
            return ('general_query', 0.5)
        
        # Get intent with highest score
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        logger.info(f"Classified intent: {best_intent[0]} (confidence: {best_intent[1]:.2f})")
        
        return best_intent
    
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """
        Extract entities from query (column names, values, etc.)
        
        Args:
            query: User query
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {
            'columns': [],
            'values': [],
            'time_references': [],
            'comparisons': []
        }
        
        # Extract quoted strings (likely column names or values)
        quoted_strings = re.findall(r'["\']([^"\']+)["\']', query)
        entities['values'].extend(quoted_strings)
        
        # Extract time references
        time_patterns = [
            r'\blast (week|month|quarter|year)\b',
            r'\b(today|yesterday|this month|last month)\b',
            r'\b\d{4}\b',  # Years
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, query.lower())
            entities['time_references'].extend(matches)
        
        # Extract comparison words
        comparison_patterns = [
            r'\b(more|less|greater|lower|higher) than\b',
            r'\btop \d+\b',
            r'\bbottom \d+\b'
        ]
        
        for pattern in comparison_patterns:
            matches = re.findall(pattern, query.lower())
            entities['comparisons'].extend(matches)
        
        return entities
    
    def needs_clarification(self, query: str, intent: str, confidence: float) -> bool:
        """
        Determine if query needs clarification
        
        Args:
            query: User query
            intent: Classified intent
            confidence: Classification confidence
            
        Returns:
            True if clarification needed
        """
        # Low confidence classification
        if confidence < 0.3:
            return True
        
        # Very short query (< 3 words)
        if len(query.split()) < 3 and intent != 'dashboard_summary':
            return True
        
        # Ambiguous pronouns without context
        ambiguous_pronouns = ['it', 'this', 'that', 'these', 'those']
        words = query.lower().split()
        
        if words[0] in ambiguous_pronouns:
            return True
        
        return False
    
    def generate_clarification_question(self, query: str, intent: str) -> str:
        """
        Generate clarification question for ambiguous queries
        
        Args:
            query: User query
            intent: Classified intent
            
        Returns:
            Clarification question
        """
        clarifications = {
            'trend_analysis': "Which specific metric or KPI would you like to see trends for?",
            'comparison': "What would you like to compare? Please specify the metrics or categories.",
            'explanation': "What specifically would you like me to explain?",
            'kpi_query': "Which KPI are you asking about?",
            'general_query': "Could you provide more details about what you're looking for?"
        }
        
        return clarifications.get(intent, "Could you please clarify your question?")
