"""
LLM Client
Handles interactions with Language Models (OpenAI, Anthropic, or Mock)
"""

import os
from typing import Optional, Dict, Any, List
import json
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Base class for LLM clients"""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                 temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """Generate text from prompt"""
        pass


class MockLLMClient(BaseLLMClient):
    """
    Mock LLM for development and testing
    Returns realistic but deterministic responses
    """
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """
        Generate mock response based on prompt keywords
        
        Args:
            prompt: User prompt
            system_prompt: System instructions (not used in mock)
            temperature: Temperature parameter (not used in mock)
            max_tokens: Max tokens (not used in mock)
            
        Returns:
            Mock generated text
        """
        logger.info("Using Mock LLM - returning templated response")
        
        prompt_lower = prompt.lower()
        
        # Executive summary generation
        if "executive summary" in prompt_lower or "summarize" in prompt_lower:
            return self._generate_executive_summary()
        
        # Insight explanation
        elif "explain" in prompt_lower and "insight" in prompt_lower:
            return self._generate_insight_explanation()
        
        # Trend analysis
        elif "trend" in prompt_lower:
            return self._generate_trend_analysis()
        
        # Correlation explanation
        elif "correlation" in prompt_lower:
            return self._generate_correlation_explanation()
        
        # Recommendation
        elif "recommend" in prompt_lower:
            return self._generate_recommendations()
        
        # KPI explanation
        elif "kpi" in prompt_lower or "dashboard" in prompt_lower:
            return self._generate_kpi_explanation()
        
        # Default response
        else:
            return self._generate_default_response()
    
    def _generate_executive_summary(self) -> str:
        return """Based on the comprehensive data analysis, here are the key findings:

**Data Quality Overview:**
The dataset contains 1,247 records across 12 variables. Missing data is present in 3 columns, with the most significant gap in the 'customer_feedback' field (23% missing values).

**Key Insights:**
1. Revenue shows a strong upward trend over the analyzed period, with a 34% increase quarter-over-quarter
2. Customer satisfaction scores correlate highly (r=0.82) with repeat purchase rate
3. Regional performance varies significantly, with the Northeast region outperforming by 28%

**Critical Findings:**
- Outlier detection identified 47 anomalous transactions requiring review
- Product Category A shows declining engagement despite stable revenue
- Customer acquisition cost increased by 15% while retention remained stable

**Recommended Actions:**
1. Investigate high-value outlier transactions for potential data quality issues
2. Address missing customer feedback through improved collection processes
3. Analyze drivers of Northeast region success for replication in other areas"""
    
    def _generate_insight_explanation(self) -> str:
        return """This insight reveals a significant pattern in the data that requires attention.

**What the data shows:**
The analysis identified a strong statistical relationship between two key variables. This correlation is not only mathematically significant (p < 0.05) but also represents a meaningful business relationship.

**Why this matters:**
Understanding this relationship can help predict outcomes and inform strategic decisions. The strength of this pattern suggests it's not due to random chance but reflects an underlying business dynamic.

**Business implications:**
Organizations can leverage this insight to optimize operations, improve forecasting accuracy, and allocate resources more effectively. The relationship indicates potential cause-and-effect dynamics that warrant further investigation.

**Next steps:**
Consider conducting a deeper dive into the causal mechanisms, segment the analysis by relevant business dimensions, and monitor this relationship over time to detect any changes in the pattern."""
    
    def _generate_trend_analysis(self) -> str:
        return """The trend analysis reveals important directional patterns in the data:

**Overall Direction:**
The metric shows a consistent upward/downward trajectory over the analyzed period. The linear regression analysis confirms this trend is statistically significant (R² = 0.76).

**Magnitude of Change:**
From the beginning to the end of the period, the metric changed by approximately 28%, representing substantial movement. The rate of change has been relatively steady, suggesting sustained underlying factors rather than temporary spikes.

**Seasonality Considerations:**
While the overall trend is clear, there are periodic fluctuations that may indicate seasonal patterns. These variations appear to follow a predictable cycle that should be factored into forecasting.

**Forward-Looking Implications:**
If current conditions persist, the trend suggests continued movement in the same direction. However, trend extrapolation should be done cautiously, considering potential market saturation, competitive factors, or economic conditions that could alter the trajectory."""
    
    def _generate_correlation_explanation(self) -> str:
        return """This correlation finding reveals an important relationship between two variables:

**Strength and Direction:**
The correlation coefficient indicates a strong relationship. This means that as one variable increases, the other tends to increase (or decrease) in a predictable way.

**Statistical Significance:**
The relationship is statistically significant, meaning it's unlikely to have occurred by chance. This gives us confidence that the pattern represents a real business phenomenon.

**Practical Interpretation:**
In business terms, this relationship suggests that changes in one metric can be used to anticipate changes in the other. This predictive power can be valuable for planning and decision-making.

**Important Caveats:**
Remember that correlation does not imply causation. While these variables move together, we cannot conclude that one causes the other without additional analysis. There may be confounding factors or a third variable driving both."""
    
    def _generate_recommendations(self) -> str:
        return """Based on the data analysis, here are prioritized recommendations:

**Immediate Actions (Next 30 Days):**
1. Address data quality issues in high-missing-value columns
2. Investigate and validate outlier transactions flagged by the analysis
3. Review processes in underperforming segments

**Short-term Initiatives (1-3 Months):**
1. Implement monitoring dashboards for key trends identified
2. Conduct root cause analysis on strong correlations discovered
3. Develop intervention strategies for declining metrics

**Strategic Considerations:**
1. Leverage successful patterns from high-performing segments
2. Invest in data collection improvements for better future analysis
3. Establish regular review cycles to track trend progression

**Risk Mitigation:**
Monitor the identified trends closely, as rapid changes could indicate emerging issues or opportunities that require quick response."""
    
    def _generate_kpi_explanation(self) -> str:
        return """Let me explain this KPI in the context of the dashboard:

**What this metric measures:**
This KPI tracks a critical business performance indicator. It's calculated using specific data points and aggregations from the underlying dataset.

**Current performance:**
The current value represents the most recent measurement. Compared to the previous period, we're seeing a change that indicates improving/declining performance.

**Why it matters:**
This metric is important because it directly relates to business objectives. Movements in this KPI can signal changes in customer behavior, operational efficiency, or market conditions.

**Dashboard context:**
The dashboard also shows related metrics that provide additional context. Looking at these together gives a more complete picture of performance.

**What drives this metric:**
Several factors influence this KPI, including operational activities, market conditions, and strategic initiatives. The analysis shows which of these factors are currently having the most impact."""
    
    def _generate_default_response(self) -> str:
        return """Based on the analysis of the available data and context:

The data reveals several important patterns and insights. The statistical analysis shows both expected relationships and some surprising findings that warrant further investigation.

Key observations include variations across different segments, temporal patterns that suggest evolving trends, and relationships between variables that have business implications.

The findings suggest opportunities for optimization and areas requiring attention. Further analysis could provide additional depth and actionable insights for decision-making."""


class OpenAIClient(BaseLLMClient):
    """OpenAI API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """Generate text using OpenAI API"""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")
        
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """Generate text using Anthropic API"""
        
        try:
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


class LLMClientFactory:
    """Factory for creating LLM clients"""
    
    @staticmethod
    def create_client(provider: str = "mock", api_key: Optional[str] = None) -> BaseLLMClient:
        """
        Create LLM client based on provider
        
        Args:
            provider: LLM provider (openai, anthropic, mock)
            api_key: API key (optional if set in environment)
            
        Returns:
            LLM client instance
        """
        provider = provider.lower()
        
        if provider == "mock":
            logger.info("Creating Mock LLM client")
            return MockLLMClient()
        
        elif provider == "openai":
            logger.info("Creating OpenAI client")
            return OpenAIClient(api_key)
        
        elif provider == "anthropic":
            logger.info("Creating Anthropic client")
            return AnthropicClient(api_key)
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
