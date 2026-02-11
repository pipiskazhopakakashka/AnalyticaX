"""
Insight Generator
Converts EDA results into human-readable insights
"""

from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsightGenerator:
    """
    Generates business insights from EDA results
    """
    
    def __init__(self, eda_results: Dict[str, Any]):
        self.eda_results = eda_results
        self.insights = []
        
    def generate_all_insights(self) -> List[Dict[str, Any]]:
        """
        Generate all insights from EDA results
        
        Returns:
            List of insight dictionaries
        """
        logger.info("Generating insights from EDA results...")
        
        self.insights = []
        
        # Generate insights from different analyses
        self._generate_missing_value_insights()
        self._generate_correlation_insights()
        self._generate_outlier_insights()
        self._generate_trend_insights()
        self._generate_distribution_insights()
        self._generate_categorical_insights()
        
        # Sort by priority
        self.insights.sort(key=lambda x: x['priority'], reverse=True)
        
        logger.info(f"Generated {len(self.insights)} insights")
        
        return self.insights
    
    def _generate_missing_value_insights(self):
        """Generate insights about missing values"""
        missing_analysis = self.eda_results.get('missing_analysis', {})
        
        if missing_analysis.get('total_missing', 0) > 0:
            by_column = missing_analysis.get('by_column', {})
            
            for col, info in by_column.items():
                if info['severity'] == 'high':
                    self.insights.append({
                        'type': 'data_quality',
                        'category': 'missing_values',
                        'priority': 8,
                        'column': col,
                        'message': f"Column '{col}' has {info['percentage']}% missing values",
                        'recommendation': f"Consider imputation or removal of '{col}' due to high missing rate",
                        'details': info
                    })
                elif info['severity'] == 'moderate':
                    self.insights.append({
                        'type': 'data_quality',
                        'category': 'missing_values',
                        'priority': 5,
                        'column': col,
                        'message': f"Column '{col}' has {info['percentage']}% missing values",
                        'recommendation': f"Review missing value pattern in '{col}'",
                        'details': info
                    })
    
    def _generate_correlation_insights(self):
        """Generate insights about correlations"""
        corr_analysis = self.eda_results.get('correlation_analysis', {})
        strong_corrs = corr_analysis.get('strong_correlations', [])
        
        for corr in strong_corrs:
            strength = corr['strength']
            direction = corr['direction']
            
            if strength == 'very_strong':
                priority = 9
                message = (f"Very strong {direction} correlation ({corr['correlation']:.3f}) "
                          f"between '{corr['variable1']}' and '{corr['variable2']}'")
                recommendation = (f"Consider potential multicollinearity or causal relationship "
                                f"between these variables")
            else:
                priority = 6
                message = (f"Strong {direction} correlation ({corr['correlation']:.3f}) "
                          f"between '{corr['variable1']}' and '{corr['variable2']}'")
                recommendation = "This relationship may be important for analysis"
            
            self.insights.append({
                'type': 'relationship',
                'category': 'correlation',
                'priority': priority,
                'columns': [corr['variable1'], corr['variable2']],
                'message': message,
                'recommendation': recommendation,
                'details': corr
            })
    
    def _generate_outlier_insights(self):
        """Generate insights about outliers"""
        outlier_analysis = self.eda_results.get('outlier_detection', {})
        
        for col, info in outlier_analysis.items():
            if info['severity'] == 'high':
                self.insights.append({
                    'type': 'data_quality',
                    'category': 'outliers',
                    'priority': 7,
                    'column': col,
                    'message': (f"Column '{col}' has {info['outlier_percentage']}% outliers "
                               f"({info['iqr_outliers']} values)"),
                    'recommendation': f"Investigate extreme values in '{col}' - may indicate errors or special cases",
                    'details': info
                })
            elif info['severity'] == 'moderate':
                self.insights.append({
                    'type': 'data_quality',
                    'category': 'outliers',
                    'priority': 4,
                    'column': col,
                    'message': f"Column '{col}' has {info['outlier_percentage']}% outliers",
                    'recommendation': f"Review outliers in '{col}' for data quality",
                    'details': info
                })
    
    def _generate_trend_insights(self):
        """Generate insights about trends"""
        trend_analysis = self.eda_results.get('trend_detection', {})
        
        for col, info in trend_analysis.items():
            if info['trend_strength'] in ['strong', 'moderate'] and info['is_significant']:
                direction = info['trend_direction']
                pct_change = info['percent_change']
                
                priority = 8 if info['trend_strength'] == 'strong' else 6
                
                self.insights.append({
                    'type': 'trend',
                    'category': 'time_series',
                    'priority': priority,
                    'column': col,
                    'message': (f"'{col}' shows a {info['trend_strength']} {direction} trend "
                               f"({pct_change:+.2f}% change)"),
                    'recommendation': (f"Monitor the {direction} trend in '{col}' - "
                                     f"R² = {info['r_squared']:.3f}"),
                    'details': info
                })
    
    def _generate_distribution_insights(self):
        """Generate insights about distributions"""
        dist_analysis = self.eda_results.get('distribution_analysis', {})
        
        for col, info in dist_analysis.items():
            if info['distribution_type'] == 'right_skewed':
                self.insights.append({
                    'type': 'distribution',
                    'category': 'shape',
                    'priority': 3,
                    'column': col,
                    'message': f"'{col}' is right-skewed (skewness: {info['skewness']:.3f})",
                    'recommendation': "Consider log transformation for right-skewed data",
                    'details': info
                })
            elif info['distribution_type'] == 'left_skewed':
                self.insights.append({
                    'type': 'distribution',
                    'category': 'shape',
                    'priority': 3,
                    'column': col,
                    'message': f"'{col}' is left-skewed (skewness: {info['skewness']:.3f})",
                    'recommendation': "Review left-skewed distribution - may indicate ceiling effects",
                    'details': info
                })
    
    def _generate_categorical_insights(self):
        """Generate insights about categorical variables"""
        cat_analysis = self.eda_results.get('categorical_analysis', {})
        
        for col, info in cat_analysis.items():
            if info['cardinality'] == 'high' and info['unique_values'] > 100:
                self.insights.append({
                    'type': 'data_structure',
                    'category': 'categorical',
                    'priority': 4,
                    'column': col,
                    'message': (f"'{col}' has very high cardinality "
                               f"({info['unique_values']} unique values)"),
                    'recommendation': (f"'{col}' may be an identifier or require grouping "
                                     "for meaningful analysis"),
                    'details': info
                })
    
    def get_top_insights(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top N insights by priority
        
        Args:
            n: Number of insights to return
            
        Returns:
            List of top insights
        """
        return self.insights[:n]
    
    def get_insights_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get insights filtered by category
        
        Args:
            category: Category to filter by
            
        Returns:
            List of insights in that category
        """
        return [i for i in self.insights if i['category'] == category]
    
    def format_insights_for_report(self) -> str:
        """
        Format insights as a text report
        
        Returns:
            Formatted string report
        """
        if not self.insights:
            return "No significant insights found."
        
        report_lines = ["=== KEY INSIGHTS ===\n"]
        
        # Group by category
        categories = {}
        for insight in self.insights:
            cat = insight['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(insight)
        
        for category, items in categories.items():
            report_lines.append(f"\n{category.upper().replace('_', ' ')}:")
            for item in items:
                report_lines.append(f"  • {item['message']}")
                report_lines.append(f"    → {item['recommendation']}")
        
        return "\n".join(report_lines)
