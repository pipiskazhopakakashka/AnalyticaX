"""
Conversational AI Chatbot Engine
Main chatbot that answers user questions about data and dashboards
"""

from typing import List, Dict, Any, Optional
import logging
from .intent_classifier import IntentClassifier
from .context_retriever import ContextRetriever
from ..utils.llm_client import BaseLLMClient, LLMClientFactory
from prompts.templates import PromptTemplates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversationHistory:
    """Manages conversation history"""
    
    def __init__(self, max_turns: int = 10):
        self.history: List[Dict[str, str]] = []
        self.max_turns = max_turns
    
    def add_turn(self, question: str, answer: str):
        """Add a conversation turn"""
        self.history.append({
            'question': question,
            'answer': answer
        })
        
        # Keep only recent history
        if len(self.history) > self.max_turns:
            self.history = self.history[-self.max_turns:]
    
    def get_recent(self, n: int = 5) -> List[Dict[str, str]]:
        """Get recent conversation turns"""
        return self.history[-n:]
    
    def clear(self):
        """Clear conversation history"""
        self.history = []
    
    def format_for_context(self, n: int = 3) -> str:
        """Format recent history for LLM context"""
        recent = self.get_recent(n)
        
        if not recent:
            return "No previous conversation"
        
        formatted = []
        for turn in recent:
            formatted.append(f"User: {turn['question']}")
            formatted.append(f"Assistant: {turn['answer']}")
            formatted.append("")
        
        return "\n".join(formatted)


class DataAnalystChatbot:
    """
    Conversational AI Data Analyst Chatbot
    """
    
    def __init__(self, 
                 llm_client: Optional[BaseLLMClient] = None,
                 use_mock: bool = True):
        
        # Initialize components
        self.intent_classifier = IntentClassifier()
        self.context_retriever = ContextRetriever()
        self.conversation_history = ConversationHistory()
        
        # Initialize LLM client
        if llm_client:
            self.llm_client = llm_client
        else:
            provider = "mock" if use_mock else "openai"
            self.llm_client = LLMClientFactory.create_client(provider)
        
        logger.info("DataAnalystChatbot initialized")
    
    def load_context(self,
                    eda_results: Optional[Dict[str, Any]] = None,
                    insights: Optional[List[Dict[str, Any]]] = None,
                    powerbi_metadata: Optional[Dict[str, Any]] = None):
        """
        Load analysis context for the chatbot
        
        Args:
            eda_results: EDA analysis results
            insights: Generated insights
            powerbi_metadata: Power BI dashboard metadata
        """
        self.context_retriever.update_context(
            eda_results=eda_results,
            insights=insights,
            powerbi_metadata=powerbi_metadata
        )
        logger.info("Context loaded successfully")
    
    def chat(self, question: str) -> str:
        """
        Main chat interface - answer user questions
        
        Args:
            question: User's question
            
        Returns:
            Chatbot's answer
        """
        logger.info(f"Processing question: {question}")
        
        # Step 1: Classify intent
        intent, confidence = self.intent_classifier.classify_intent(question)
        
        # Step 2: Extract entities
        entities = self.intent_classifier.extract_entities(question)
        
        # Step 3: Check if clarification needed
        if self.intent_classifier.needs_clarification(question, intent, confidence):
            clarification = self.intent_classifier.generate_clarification_question(
                question, intent
            )
            self.conversation_history.add_turn(question, clarification)
            return clarification
        
        # Step 4: Retrieve relevant context
        context = self.context_retriever.retrieve_for_query(
            question, intent, entities
        )
        
        # Step 5: Generate response using LLM
        answer = self._generate_response(question, context)
        
        # Step 6: Update conversation history
        self.conversation_history.add_turn(question, answer)
        
        return answer
    
    def _generate_response(self, question: str, context: Dict[str, Any]) -> str:
        """
        Generate response using LLM
        
        Args:
            question: User question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        # Format context for LLM
        dataset_context = str(context.get('dataset_context', 'No dataset context'))
        insights_context = str(context.get('insights_context', 'No insights available'))
        dashboard_context = str(context.get('dashboard_context', 'No dashboard data'))
        
        # Get conversation history
        history = self.conversation_history.format_for_context()
        
        # Build prompt
        prompt = PromptTemplates.format_template(
            PromptTemplates.CHATBOT_RESPONSE,
            question=question,
            history=history,
            dataset_context=dataset_context,
            insights_context=insights_context,
            dashboard_context=dashboard_context
        )
        
        # Get system prompt
        system_prompt = PromptTemplates.CHATBOT_SYSTEM
        
        # Generate response
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.strip()
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error processing your question. Please try rephrasing it."
    
    def explain_insight(self, insight: Dict[str, Any]) -> str:
        """
        Explain a specific insight in detail
        
        Args:
            insight: Insight dictionary
            
        Returns:
            Detailed explanation
        """
        prompt = PromptTemplates.format_template(
            PromptTemplates.INSIGHT_EXPLANATION,
            insight=insight.get('message', ''),
            context=insight.get('details', {})
        )
        
        try:
            explanation = self.llm_client.generate(
                prompt=prompt,
                system_prompt=PromptTemplates.SYSTEM_ANALYST
            )
            return explanation.strip()
        
        except Exception as e:
            logger.error(f"Error explaining insight: {e}")
            return insight.get('recommendation', 'Unable to generate explanation')
    
    def explain_kpi(self, kpi_name: str) -> str:
        """
        Explain a specific KPI from Power BI dashboard
        
        Args:
            kpi_name: Name of the KPI
            
        Returns:
            KPI explanation
        """
        # Get KPI context
        context = self.context_retriever._get_kpi_context(
            kpi_name, {}
        )
        
        if not context.get('kpis'):
            return f"I don't have information about the KPI '{kpi_name}'"
        
        kpi_data = context['kpis'][0]
        
        prompt = PromptTemplates.format_template(
            PromptTemplates.KPI_EXPLANATION,
            kpi_details=kpi_data,
            dashboard_context=self.context_retriever.powerbi_metadata,
            related_data={}
        )
        
        try:
            explanation = self.llm_client.generate(
                prompt=prompt,
                system_prompt=PromptTemplates.SYSTEM_ANALYST
            )
            return explanation.strip()
        
        except Exception as e:
            logger.error(f"Error explaining KPI: {e}")
            return f"KPI '{kpi_name}': {kpi_data.get('value', 'N/A')}"
    
    def summarize_dashboard(self) -> str:
        """
        Generate dashboard summary
        
        Returns:
            Dashboard summary
        """
        if not self.context_retriever.powerbi_metadata:
            return "No Power BI dashboard data available"
        
        metadata = self.context_retriever.powerbi_metadata
        
        prompt = PromptTemplates.format_template(
            PromptTemplates.DASHBOARD_SUMMARY,
            dashboard_name=metadata.get('dashboard_name', 'Unknown'),
            kpis=metadata.get('kpis', []),
            filters=metadata.get('filters', {}),
            visualizations=metadata.get('visualizations', [])
        )
        
        try:
            summary = self.llm_client.generate(
                prompt=prompt,
                system_prompt=PromptTemplates.SYSTEM_ANALYST
            )
            return summary.strip()
        
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {e}")
            return "Unable to generate dashboard summary"
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
