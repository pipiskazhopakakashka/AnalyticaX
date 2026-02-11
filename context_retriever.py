"""
Context Retriever
Retrieves relevant context for answering user questions (RAG-style)
"""

from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextRetriever:
    """
    Retrieves relevant context from dataset and dashboard metadata
    """
    
    def __init__(self, 
                 eda_results: Optional[Dict[str, Any]] = None,
                 insights: Optional[List[Dict[str, Any]]] = None,
                 powerbi_metadata: Optional[Dict[str, Any]] = None):
        
        self.eda_results = eda_results or {}
        self.insights = insights or []
        self.powerbi_metadata = powerbi_metadata or {}
    
    def update_context(self,
                      eda_results: Optional[Dict[str, Any]] = None,
                      insights: Optional[List[Dict[str, Any]]] = None,
                      powerbi_metadata: Optional[Dict[str, Any]] = None):
        """Update the available context"""
        if eda_results:
            self.eda_results = eda_results
        if insights:
            self.insights = insights
        if powerbi_metadata:
            self.powerbi_metadata = powerbi_metadata
    
    def retrieve_for_query(self, query: str, intent: str, 
                          entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User query
            intent: Classified intent
            entities: Extracted entities
            
        Returns:
            Dictionary containing relevant context
        """
        logger.info(f"Retrieving context for intent: {intent}")
        
        context = {
            'intent': intent,
            'dataset_context': {},
            'insights_context': [],
            'dashboard_context': {}
        }
        
        # Route to appropriate retrieval method
        if intent == 'trend_analysis':
            context['dataset_context'] = self._get_trend_context(query, entities)
            context['insights_context'] = self._get_trend_insights()
        
        elif intent == 'comparison':
            context['dataset_context'] = self._get_comparison_context(query, entities)
        
        elif intent == 'explanation':
            context['insights_context'] = self._get_explanation_insights(query)
            context['dataset_context'] = self._get_correlation_context()
        
        elif intent == 'kpi_query':
            context['dashboard_context'] = self._get_kpi_context(query, entities)
        
        elif intent == 'dashboard_summary':
            context['dashboard_context'] = self.powerbi_metadata
            context['insights_context'] = self.insights[:5]  # Top 5 insights
        
        elif intent == 'anomaly_detection':
            context['dataset_context'] = self._get_outlier_context()
            context['insights_context'] = self._get_anomaly_insights()
        
        else:  # general_query
            context['dataset_context'] = self._get_general_stats()
            context['insights_context'] = self.insights[:3]
            context['dashboard_context'] = self._get_top_kpis()
        
        return context
    
    def _get_trend_context(self, query: str, entities: Dict) -> Dict[str, Any]:
        """Get context related to trends"""
        trend_data = self.eda_results.get('trend_detection', {})
        
        # Try to match specific column from query
        query_lower = query.lower()
        relevant_trends = {}
        
        for column, trend_info in trend_data.items():
            if column.lower() in query_lower:
                relevant_trends[column] = trend_info
        
        # If no specific match, return all significant trends
        if not relevant_trends:
            relevant_trends = {
                col: info for col, info in trend_data.items()
                if info.get('trend_strength') in ['strong', 'moderate']
            }
        
        return {
            'type': 'trends',
            'data': relevant_trends
        }
    
    def _get_trend_insights(self) -> List[Dict[str, Any]]:
        """Get insights related to trends"""
        return [
            insight for insight in self.insights
            if insight.get('type') == 'trend'
        ]
    
    def _get_comparison_context(self, query: str, entities: Dict) -> Dict[str, Any]:
        """Get context for comparison queries"""
        stats = self.eda_results.get('descriptive_stats', {})
        categorical = self.eda_results.get('categorical_analysis', {})
        
        return {
            'type': 'comparison',
            'numeric_stats': stats,
            'categorical_stats': categorical
        }
    
    def _get_explanation_insights(self, query: str) -> List[Dict[str, Any]]:
        """Get insights that help explain phenomena"""
        query_lower = query.lower()
        
        # Return insights mentioned in query
        relevant_insights = []
        
        for insight in self.insights:
            # Check if insight is about columns mentioned in query
            if 'column' in insight:
                if insight['column'].lower() in query_lower:
                    relevant_insights.append(insight)
            elif 'columns' in insight:
                for col in insight['columns']:
                    if col.lower() in query_lower:
                        relevant_insights.append(insight)
                        break
        
        # If no specific insights found, return high-priority ones
        if not relevant_insights:
            relevant_insights = [
                i for i in self.insights if i.get('priority', 0) >= 7
            ][:3]
        
        return relevant_insights
    
    def _get_correlation_context(self) -> Dict[str, Any]:
        """Get correlation context for explanations"""
        corr_analysis = self.eda_results.get('correlation_analysis', {})
        
        return {
            'type': 'correlations',
            'data': corr_analysis.get('strong_correlations', [])
        }
    
    def _get_kpi_context(self, query: str, entities: Dict) -> Dict[str, Any]:
        """Get context about specific KPIs"""
        if not self.powerbi_metadata:
            return {'message': 'No Power BI data available'}
        
        query_lower = query.lower()
        kpis = self.powerbi_metadata.get('kpis', [])
        
        # Find matching KPI
        matching_kpis = []
        for kpi in kpis:
            kpi_name = kpi.get('name', '').lower()
            if kpi_name in query_lower or any(word in kpi_name for word in query_lower.split()):
                matching_kpis.append(kpi)
        
        if matching_kpis:
            return {
                'type': 'kpi',
                'kpis': matching_kpis
            }
        else:
            # Return all KPIs if no match
            return {
                'type': 'kpi',
                'kpis': kpis[:5],  # Top 5
                'note': 'Showing top KPIs (no specific match found)'
            }
    
    def _get_outlier_context(self) -> Dict[str, Any]:
        """Get context about outliers and anomalies"""
        outlier_data = self.eda_results.get('outlier_detection', {})
        
        # Filter for significant outliers
        significant_outliers = {
            col: info for col, info in outlier_data.items()
            if info.get('severity') in ['moderate', 'high']
        }
        
        return {
            'type': 'outliers',
            'data': significant_outliers
        }
    
    def _get_anomaly_insights(self) -> List[Dict[str, Any]]:
        """Get insights related to anomalies"""
        return [
            insight for insight in self.insights
            if insight.get('category') == 'outliers'
        ]
    
    def _get_general_stats(self) -> Dict[str, Any]:
        """Get general dataset statistics"""
        return {
            'type': 'general',
            'descriptive_stats': self.eda_results.get('descriptive_stats', {}),
            'aggregated_metrics': self.eda_results.get('aggregated_metrics', {})
        }
    
    def _get_top_kpis(self) -> Dict[str, Any]:
        """Get top KPIs from dashboard"""
        if not self.powerbi_metadata:
            return {}
        
        kpis = self.powerbi_metadata.get('kpis', [])
        
        return {
            'type': 'kpi_summary',
            'top_kpis': kpis[:5]
        }
    
    def format_context_for_llm(self, context: Dict[str, Any]) -> str:
        """
        Format retrieved context for LLM consumption
        
        Args:
            context: Retrieved context dictionary
            
        Returns:
            Formatted context string
        """
        lines = []
        
        # Dataset context
        if context.get('dataset_context'):
            lines.append("=== DATASET CONTEXT ===")
            lines.append(str(context['dataset_context']))
            lines.append("")
        
        # Insights context
        if context.get('insights_context'):
            lines.append("=== RELEVANT INSIGHTS ===")
            for insight in context['insights_context']:
                lines.append(f"- {insight.get('message', '')}")
                lines.append(f"  {insight.get('recommendation', '')}")
            lines.append("")
        
        # Dashboard context
        if context.get('dashboard_context'):
            lines.append("=== DASHBOARD CONTEXT ===")
            dash_ctx = context['dashboard_context']
            
            if 'kpis' in dash_ctx:
                lines.append("KPIs:")
                for kpi in dash_ctx['kpis']:
                    lines.append(f"  - {kpi.get('name')}: {kpi.get('value')}")
            else:
                lines.append(str(dash_ctx))
            lines.append("")
        
        return "\n".join(lines)
