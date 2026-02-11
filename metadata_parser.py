"""
Power BI Integration Module
Parses and interprets Power BI dashboard metadata
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PowerBIMetadataParser:
    """
    Parses Power BI dashboard metadata exported as JSON
    """
    
    def __init__(self, metadata_path: Optional[str] = None):
        self.metadata = {}
        self.kpis = []
        self.visualizations = []
        self.filters = {}
        
        if metadata_path:
            self.load_metadata(metadata_path)
    
    def load_metadata(self, metadata_path: str) -> Dict[str, Any]:
        """
        Load Power BI metadata from JSON file
        
        Args:
            metadata_path: Path to metadata JSON file
            
        Returns:
            Parsed metadata dictionary
        """
        logger.info(f"Loading Power BI metadata from {metadata_path}")
        
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        
        # Parse components
        self.kpis = self.metadata.get('kpis', [])
        self.visualizations = self.metadata.get('visualizations', [])
        self.filters = self.metadata.get('filters', {})
        
        logger.info(f"Loaded {len(self.kpis)} KPIs and {len(self.visualizations)} visualizations")
        
        return self.metadata
    
    def get_kpi(self, kpi_name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific KPI by name
        
        Args:
            kpi_name: Name of the KPI
            
        Returns:
            KPI dictionary or None
        """
        for kpi in self.kpis:
            if kpi.get('name', '').lower() == kpi_name.lower():
                return kpi
        return None
    
    def get_all_kpis(self) -> List[Dict[str, Any]]:
        """
        Get all KPIs
        
        Returns:
            List of KPI dictionaries
        """
        return self.kpis
    
    def get_kpi_summary(self) -> str:
        """
        Get a text summary of all KPIs
        
        Returns:
            Formatted string summary
        """
        if not self.kpis:
            return "No KPIs available"
        
        summary_lines = ["=== POWER BI KPIs ===\n"]
        
        for kpi in self.kpis:
            name = kpi.get('name', 'Unknown')
            value = kpi.get('value', 'N/A')
            trend = kpi.get('trend', {})
            
            trend_direction = trend.get('direction', 'stable')
            trend_value = trend.get('value', 0)
            
            summary_lines.append(f"{name}: {value}")
            summary_lines.append(f"  Trend: {trend_direction} ({trend_value:+.2f}%)")
            
            if 'target' in kpi:
                target = kpi['target']
                variance = ((value - target) / target * 100) if target != 0 else 0
                summary_lines.append(f"  Target: {target} (variance: {variance:+.2f}%)")
            
            summary_lines.append("")
        
        return "\n".join(summary_lines)
    
    def analyze_kpi_performance(self, kpi_name: str) -> Dict[str, Any]:
        """
        Analyze a specific KPI's performance
        
        Args:
            kpi_name: Name of the KPI to analyze
            
        Returns:
            Performance analysis dictionary
        """
        kpi = self.get_kpi(kpi_name)
        
        if not kpi:
            return {"error": f"KPI '{kpi_name}' not found"}
        
        value = kpi.get('value', 0)
        target = kpi.get('target')
        trend = kpi.get('trend', {})
        
        analysis = {
            "name": kpi_name,
            "current_value": value,
            "performance_status": "unknown"
        }
        
        # Compare to target
        if target is not None:
            variance = ((value - target) / target * 100) if target != 0 else 0
            analysis['target'] = target
            analysis['variance_pct'] = round(variance, 2)
            
            if variance >= 0:
                analysis['performance_status'] = 'above_target'
            elif variance >= -5:
                analysis['performance_status'] = 'near_target'
            else:
                analysis['performance_status'] = 'below_target'
        
        # Analyze trend
        if trend:
            trend_direction = trend.get('direction', 'stable')
            trend_value = trend.get('value', 0)
            
            analysis['trend'] = {
                'direction': trend_direction,
                'magnitude': abs(trend_value),
                'severity': self._classify_trend_severity(abs(trend_value))
            }
        
        return analysis
    
    def _classify_trend_severity(self, pct: float) -> str:
        """Classify trend severity"""
        if pct < 5:
            return 'minor'
        elif pct < 10:
            return 'moderate'
        else:
            return 'significant'
    
    def get_dashboard_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard overview
        
        Returns:
            Dashboard overview dictionary
        """
        overview = {
            "dashboard_name": self.metadata.get('dashboard_name', 'Unknown'),
            "last_refresh": self.metadata.get('last_refresh', 'Unknown'),
            "total_kpis": len(self.kpis),
            "total_visualizations": len(self.visualizations),
            "active_filters": self.filters
        }
        
        # Summarize KPI performance
        kpi_summary = {
            'above_target': 0,
            'near_target': 0,
            'below_target': 0,
            'no_target': 0
        }
        
        for kpi in self.kpis:
            analysis = self.analyze_kpi_performance(kpi['name'])
            status = analysis.get('performance_status', 'unknown')
            
            if status in kpi_summary:
                kpi_summary[status] += 1
            else:
                kpi_summary['no_target'] += 1
        
        overview['kpi_performance_summary'] = kpi_summary
        
        return overview
    
    def find_related_kpis(self, kpi_name: str) -> List[Dict[str, Any]]:
        """
        Find KPIs related to a given KPI
        
        Args:
            kpi_name: Name of the KPI
            
        Returns:
            List of related KPIs
        """
        kpi = self.get_kpi(kpi_name)
        
        if not kpi:
            return []
        
        # Get category/tags
        kpi_category = kpi.get('category', '')
        kpi_tags = set(kpi.get('tags', []))
        
        related = []
        
        for other_kpi in self.kpis:
            if other_kpi['name'] == kpi_name:
                continue
            
            # Check for same category
            if other_kpi.get('category') == kpi_category:
                related.append(other_kpi)
                continue
            
            # Check for shared tags
            other_tags = set(other_kpi.get('tags', []))
            if kpi_tags & other_tags:  # Intersection
                related.append(other_kpi)
        
        return related
    
    def export_context_for_llm(self) -> str:
        """
        Export dashboard context in LLM-friendly format
        
        Returns:
            Formatted context string
        """
        context_lines = [
            f"Dashboard: {self.metadata.get('dashboard_name', 'Unknown')}",
            f"Last Updated: {self.metadata.get('last_refresh', 'Unknown')}",
            "\nKEY PERFORMANCE INDICATORS:\n"
        ]
        
        for kpi in self.kpis:
            context_lines.append(f"- {kpi['name']}: {kpi.get('value', 'N/A')}")
            
            if 'trend' in kpi:
                trend = kpi['trend']
                context_lines.append(
                    f"  Trend: {trend.get('direction', 'stable')} "
                    f"({trend.get('value', 0):+.2f}%)"
                )
            
            if 'description' in kpi:
                context_lines.append(f"  Description: {kpi['description']}")
            
            context_lines.append("")
        
        if self.filters:
            context_lines.append("\nAPPLIED FILTERS:")
            for filter_name, filter_value in self.filters.items():
                context_lines.append(f"- {filter_name}: {filter_value}")
        
        return "\n".join(context_lines)


class DashboardExplainer:
    """
    Explains Power BI dashboards in natural language
    """
    
    def __init__(self, metadata_parser: PowerBIMetadataParser):
        self.parser = metadata_parser
    
    def explain_kpi(self, kpi_name: str) -> str:
        """
        Generate natural language explanation of a KPI
        
        Args:
            kpi_name: Name of the KPI
            
        Returns:
            Explanation string
        """
        analysis = self.parser.analyze_kpi_performance(kpi_name)
        
        if 'error' in analysis:
            return analysis['error']
        
        explanation = [f"**{kpi_name}**"]
        explanation.append(f"Current Value: {analysis['current_value']}")
        
        if 'target' in analysis:
            target = analysis['target']
            variance = analysis['variance_pct']
            
            if variance >= 0:
                explanation.append(
                    f"Performance: {variance:.1f}% above target ({target})"
                )
            else:
                explanation.append(
                    f"Performance: {abs(variance):.1f}% below target ({target})"
                )
        
        if 'trend' in analysis:
            trend = analysis['trend']
            direction = trend['direction']
            magnitude = trend['magnitude']
            
            explanation.append(
                f"Trend: {direction.capitalize()} by {magnitude:.1f}%"
            )
        
        return "\n".join(explanation)
    
    def explain_dashboard(self) -> str:
        """
        Generate comprehensive dashboard explanation
        
        Returns:
            Dashboard explanation string
        """
        overview = self.parser.get_dashboard_overview()
        
        explanation = [
            f"# {overview['dashboard_name']}",
            f"Last Updated: {overview['last_refresh']}",
            "",
            "## Performance Summary",
            f"Total KPIs: {overview['total_kpis']}"
        ]
        
        perf_summary = overview['kpi_performance_summary']
        
        if perf_summary['above_target'] > 0:
            explanation.append(
                f"✓ {perf_summary['above_target']} KPIs above target"
            )
        
        if perf_summary['below_target'] > 0:
            explanation.append(
                f"⚠ {perf_summary['below_target']} KPIs below target"
            )
        
        explanation.append("\n## Key Metrics")
        
        for kpi in self.parser.get_all_kpis()[:5]:  # Top 5
            explanation.append(self.explain_kpi(kpi['name']))
            explanation.append("")
        
        return "\n".join(explanation)
