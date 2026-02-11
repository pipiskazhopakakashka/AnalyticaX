"""
Prompt Templates
Structured prompts for different LLM tasks
"""

from typing import Dict, Any
import json


class PromptTemplates:
    """Collection of prompt templates for LLM interactions"""
    
    SYSTEM_ANALYST = """You are an expert data analyst with deep knowledge of statistics, business intelligence, and data storytelling. Your role is to:

1. Analyze data comprehensively and objectively
2. Explain complex statistical concepts in simple business terms
3. Provide actionable insights and recommendations
4. Communicate findings clearly to non-technical stakeholders
5. Consider business context when interpreting data

Always base your responses on the data and context provided. Be precise with numbers and clear about confidence levels."""
    
    EXECUTIVE_SUMMARY = """Based on the following data analysis results, create a comprehensive executive summary.

**EDA RESULTS:**
{eda_results}

**INSIGHTS:**
{insights}

Please provide:
1. **Overview**: Brief description of the dataset and analysis scope
2. **Key Findings**: 3-5 most important discoveries
3. **Critical Issues**: Any data quality or business concerns identified
4. **Opportunities**: Areas of strength or potential improvement
5. **Recommendations**: Top 3 actionable next steps

Keep the summary concise but informative, suitable for executive leadership."""
    
    INSIGHT_EXPLANATION = """Explain the following data insight in clear, business-friendly language:

**INSIGHT:**
{insight}

**CONTEXT:**
{context}

Please explain:
1. What the data shows (in simple terms)
2. Why this pattern exists (potential root causes)
3. What it means for the business (implications)
4. What actions should be considered (recommendations)

Use analogies or examples where helpful. Avoid jargon."""
    
    TREND_ANALYSIS = """Analyze and explain the following trend:

**METRIC:** {metric_name}
**TREND DATA:**
{trend_data}

**STATISTICAL SUMMARY:**
- Direction: {direction}
- Magnitude: {magnitude}
- Strength: {strength}
- Significance: {significance}

Provide:
1. Clear description of the trend
2. Possible drivers or causes
3. Future implications if trend continues
4. Recommendations for action

Be specific about timeframes and magnitudes."""
    
    CORRELATION_EXPLANATION = """Explain this correlation finding to a business audience:

**VARIABLES:**
- Variable 1: {var1}
- Variable 2: {var2}

**CORRELATION DETAILS:**
- Coefficient: {coefficient}
- Strength: {strength}
- Direction: {direction}
- Significance: {significance}

Explain:
1. What this relationship means in business terms
2. Potential reasons for this relationship
3. How this insight can be used practically
4. Important caveats (correlation vs causation)

Make it actionable and clear."""
    
    CHATBOT_SYSTEM = """You are a conversational data analyst assistant. You help users understand their data and dashboards through natural conversation.

**YOUR CAPABILITIES:**
- Answer questions about datasets, trends, and insights
- Explain KPIs and dashboard metrics
- Provide data-driven recommendations
- Clarify statistical concepts

**YOUR CONSTRAINTS:**
- Only use information from the provided context
- Clearly state when you don't have enough information
- Ask clarifying questions when the user's intent is unclear
- Keep responses concise but complete

**CONVERSATION STYLE:**
- Friendly and professional
- Use business language, not statistical jargon
- Provide specific numbers and examples
- Offer to elaborate if needed"""
    
    CHATBOT_RESPONSE = """Answer the user's question using the provided context.

**USER QUESTION:**
{question}

**CONVERSATION HISTORY:**
{history}

**AVAILABLE CONTEXT:**

Dataset Information:
{dataset_context}

Recent Insights:
{insights_context}

Power BI Dashboard Context:
{dashboard_context}

**INSTRUCTIONS:**
1. Directly answer the user's question
2. Use specific data points from the context
3. If you need clarification, ask
4. If information is not in the context, say so
5. Keep response conversational but precise

Your response:"""
    
    KPI_EXPLANATION = """Explain this KPI from the Power BI dashboard:

**KPI DETAILS:**
{kpi_details}

**DASHBOARD CONTEXT:**
{dashboard_context}

**RELATED DATA:**
{related_data}

Provide:
1. What this KPI measures (in business terms)
2. Current performance assessment
3. Key drivers of current value
4. Comparison to benchmarks or targets (if available)
5. Actionable insights

Explain as if speaking to a business stakeholder."""
    
    DASHBOARD_SUMMARY = """Summarize this Power BI dashboard for the user:

**DASHBOARD NAME:** {dashboard_name}

**KPIs:**
{kpis}

**FILTERS APPLIED:**
{filters}

**VISUALIZATIONS:**
{visualizations}

Provide:
1. Purpose and scope of this dashboard
2. Overall performance summary
3. Key takeaways (3-5 points)
4. Areas requiring attention
5. Recommended next steps

Make it accessible to non-technical users."""
    
    ANOMALY_EXPLANATION = """Explain this data anomaly:

**ANOMALY DETAILS:**
{anomaly_details}

**NORMAL PATTERN:**
{normal_pattern}

**DEVIATION:**
{deviation}

Explain:
1. What makes this an anomaly
2. Potential causes (data error vs real phenomenon)
3. Business implications
4. Recommended investigation steps

Be clear about uncertainty and confidence levels."""
    
    RECOMMENDATION_GENERATION = """Generate actionable recommendations based on this analysis:

**ANALYSIS SUMMARY:**
{analysis_summary}

**KEY FINDINGS:**
{key_findings}

**BUSINESS CONTEXT:**
{business_context}

Provide:
1. **Immediate Actions** (next 30 days)
2. **Short-term Initiatives** (1-3 months)
3. **Strategic Considerations** (3-12 months)

For each recommendation:
- Be specific and actionable
- Explain expected impact
- Note any prerequisites or dependencies
- Prioritize by potential value

Focus on practical, implementable suggestions."""
    
    @staticmethod
    def format_template(template: str, **kwargs) -> str:
        """
        Format a template with provided values
        
        Args:
            template: Template string
            **kwargs: Values to insert
            
        Returns:
            Formatted prompt
        """
        # Convert complex objects to JSON strings
        formatted_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, (dict, list)):
                formatted_kwargs[key] = json.dumps(value, indent=2)
            else:
                formatted_kwargs[key] = str(value)
        
        return template.format(**formatted_kwargs)
    
    @staticmethod
    def get_template(name: str) -> str:
        """
        Get a template by name
        
        Args:
            name: Template name
            
        Returns:
            Template string
        """
        templates = {
            'system_analyst': PromptTemplates.SYSTEM_ANALYST,
            'executive_summary': PromptTemplates.EXECUTIVE_SUMMARY,
            'insight_explanation': PromptTemplates.INSIGHT_EXPLANATION,
            'trend_analysis': PromptTemplates.TREND_ANALYSIS,
            'correlation_explanation': PromptTemplates.CORRELATION_EXPLANATION,
            'chatbot_system': PromptTemplates.CHATBOT_SYSTEM,
            'chatbot_response': PromptTemplates.CHATBOT_RESPONSE,
            'kpi_explanation': PromptTemplates.KPI_EXPLANATION,
            'dashboard_summary': PromptTemplates.DASHBOARD_SUMMARY,
            'anomaly_explanation': PromptTemplates.ANOMALY_EXPLANATION,
            'recommendation_generation': PromptTemplates.RECOMMENDATION_GENERATION
        }
        
        return templates.get(name, "")
