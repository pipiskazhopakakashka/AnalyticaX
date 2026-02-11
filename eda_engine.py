"""
Exploratory Data Analysis Engine
Performs comprehensive automated EDA on datasets
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from scipy import stats
from sklearn.preprocessing import StandardScaler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EDAEngine:
    """
    Automated Exploratory Data Analysis Engine
    """
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.results = {}
        
    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Run complete EDA analysis
        
        Returns:
            Dictionary containing all analysis results
        """
        logger.info("Starting comprehensive EDA...")
        
        self.results = {
            "descriptive_stats": self.get_descriptive_statistics(),
            "missing_analysis": self.analyze_missing_values(),
            "correlation_analysis": self.analyze_correlations(),
            "distribution_analysis": self.analyze_distributions(),
            "categorical_analysis": self.analyze_categorical(),
            "outlier_detection": self.detect_outliers(),
            "trend_detection": self.detect_trends(),
            "aggregated_metrics": self.compute_aggregated_metrics()
        }
        
        logger.info("EDA completed successfully")
        
        return self.results
    
    def get_descriptive_statistics(self) -> Dict[str, Any]:
        """Get descriptive statistics for numerical columns"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return {"message": "No numeric columns found"}
        
        stats_df = self.data[numeric_cols].describe()
        
        # Add additional statistics
        stats_dict = stats_df.to_dict()
        
        for col in numeric_cols:
            stats_dict[col]['variance'] = float(self.data[col].var())
            stats_dict[col]['skewness'] = float(self.data[col].skew())
            stats_dict[col]['kurtosis'] = float(self.data[col].kurtosis())
            stats_dict[col]['coefficient_of_variation'] = (
                float(self.data[col].std() / self.data[col].mean()) 
                if self.data[col].mean() != 0 else 0
            )
        
        return stats_dict
    
    def analyze_missing_values(self) -> Dict[str, Any]:
        """Analyze missing values in the dataset"""
        missing_counts = self.data.isnull().sum()
        total_rows = len(self.data)
        
        missing_analysis = {
            "total_missing": int(missing_counts.sum()),
            "by_column": {}
        }
        
        for col in self.data.columns:
            missing_count = int(missing_counts[col])
            missing_pct = (missing_count / total_rows) * 100
            
            if missing_count > 0:
                missing_analysis["by_column"][col] = {
                    "count": missing_count,
                    "percentage": round(missing_pct, 2),
                    "severity": self._classify_missing_severity(missing_pct)
                }
        
        return missing_analysis
    
    def _classify_missing_severity(self, pct: float) -> str:
        """Classify missing value severity"""
        if pct < 5:
            return "low"
        elif pct < 20:
            return "moderate"
        else:
            return "high"
    
    def analyze_correlations(self) -> Dict[str, Any]:
        """Analyze correlations between numeric variables"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {"message": "Insufficient numeric columns for correlation"}
        
        corr_matrix = self.data[numeric_cols].corr()
        
        # Find strong correlations
        strong_correlations = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        "variable1": col1,
                        "variable2": col2,
                        "correlation": round(float(corr_value), 3),
                        "strength": self._classify_correlation_strength(corr_value),
                        "direction": "positive" if corr_value > 0 else "negative"
                    })
        
        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "strong_correlations": strong_correlations
        }
    
    def _classify_correlation_strength(self, corr: float) -> str:
        """Classify correlation strength"""
        abs_corr = abs(corr)
        if abs_corr > 0.9:
            return "very_strong"
        elif abs_corr > 0.7:
            return "strong"
        elif abs_corr > 0.5:
            return "moderate"
        else:
            return "weak"
    
    def analyze_distributions(self) -> Dict[str, Any]:
        """Analyze distributions of numeric variables"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        distributions = {}
        
        for col in numeric_cols:
            col_data = self.data[col].dropna()
            
            if len(col_data) == 0:
                continue
            
            # Normality test (Shapiro-Wilk for small samples, Anderson-Darling for larger)
            if len(col_data) < 5000:
                _, p_value = stats.shapiro(col_data)
                normality_test = "shapiro"
            else:
                result = stats.anderson(col_data)
                p_value = 0.05 if result.statistic > result.critical_values[2] else 0.1
                normality_test = "anderson"
            
            distributions[col] = {
                "is_normal": p_value > 0.05,
                "normality_test": normality_test,
                "p_value": round(float(p_value), 4),
                "skewness": round(float(col_data.skew()), 3),
                "kurtosis": round(float(col_data.kurtosis()), 3),
                "distribution_type": self._classify_distribution(col_data)
            }
        
        return distributions
    
    def _classify_distribution(self, data: pd.Series) -> str:
        """Classify distribution type"""
        skew = data.skew()
        kurt = data.kurtosis()
        
        if abs(skew) < 0.5 and abs(kurt) < 1:
            return "approximately_normal"
        elif skew > 1:
            return "right_skewed"
        elif skew < -1:
            return "left_skewed"
        elif kurt > 3:
            return "heavy_tailed"
        else:
            return "unknown"
    
    def analyze_categorical(self) -> Dict[str, Any]:
        """Analyze categorical variables"""
        categorical_cols = self.data.select_dtypes(
            include=['object', 'category']
        ).columns
        
        categorical_analysis = {}
        
        for col in categorical_cols:
            value_counts = self.data[col].value_counts()
            
            categorical_analysis[col] = {
                "unique_values": int(self.data[col].nunique()),
                "most_common": value_counts.head(5).to_dict(),
                "cardinality": self._classify_cardinality(
                    self.data[col].nunique(), 
                    len(self.data)
                )
            }
        
        return categorical_analysis
    
    def _classify_cardinality(self, unique_count: int, total_count: int) -> str:
        """Classify cardinality of categorical variable"""
        ratio = unique_count / total_count
        
        if ratio > 0.9:
            return "high"  # Likely an identifier
        elif unique_count < 10:
            return "low"
        elif unique_count < 50:
            return "moderate"
        else:
            return "high"
    
    def detect_outliers(self) -> Dict[str, Any]:
        """Detect outliers using IQR and Z-score methods"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        outlier_analysis = {}
        
        for col in numeric_cols:
            col_data = self.data[col].dropna()
            
            if len(col_data) == 0:
                continue
            
            # IQR method
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            
            iqr_outliers = col_data[
                (col_data < Q1 - 1.5 * IQR) | (col_data > Q3 + 1.5 * IQR)
            ]
            
            # Z-score method
            z_scores = np.abs(stats.zscore(col_data))
            z_outliers = col_data[z_scores > 3]
            
            outlier_analysis[col] = {
                "iqr_outliers": int(len(iqr_outliers)),
                "z_score_outliers": int(len(z_outliers)),
                "outlier_percentage": round(
                    (len(iqr_outliers) / len(col_data)) * 100, 2
                ),
                "severity": self._classify_outlier_severity(
                    len(iqr_outliers) / len(col_data)
                )
            }
        
        return outlier_analysis
    
    def _classify_outlier_severity(self, pct: float) -> str:
        """Classify outlier severity"""
        if pct < 0.01:
            return "low"
        elif pct < 0.05:
            return "moderate"
        else:
            return "high"
    
    def detect_trends(self) -> Dict[str, Any]:
        """Detect trends in time series or sequential data"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        trend_analysis = {}
        
        for col in numeric_cols:
            col_data = self.data[col].dropna()
            
            if len(col_data) < 10:
                continue
            
            # Simple linear trend
            x = np.arange(len(col_data))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, col_data)
            
            # Calculate percent change
            if col_data.iloc[0] != 0:
                pct_change = ((col_data.iloc[-1] - col_data.iloc[0]) / 
                             abs(col_data.iloc[0])) * 100
            else:
                pct_change = 0
            
            trend_analysis[col] = {
                "trend_direction": "increasing" if slope > 0 else "decreasing",
                "slope": round(float(slope), 4),
                "r_squared": round(float(r_value ** 2), 4),
                "trend_strength": self._classify_trend_strength(r_value ** 2),
                "percent_change": round(float(pct_change), 2),
                "is_significant": p_value < 0.05
            }
        
        return trend_analysis
    
    def _classify_trend_strength(self, r_squared: float) -> str:
        """Classify trend strength based on R-squared"""
        if r_squared > 0.7:
            return "strong"
        elif r_squared > 0.4:
            return "moderate"
        else:
            return "weak"
    
    def compute_aggregated_metrics(self) -> Dict[str, Any]:
        """Compute aggregated metrics for dashboard creation"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        metrics = {
            "total_records": len(self.data),
            "numeric_summaries": {},
            "categorical_summaries": {}
        }
        
        # Numeric aggregations
        for col in numeric_cols:
            metrics["numeric_summaries"][col] = {
                "sum": float(self.data[col].sum()),
                "mean": float(self.data[col].mean()),
                "median": float(self.data[col].median()),
                "min": float(self.data[col].min()),
                "max": float(self.data[col].max()),
                "std": float(self.data[col].std())
            }
        
        # Categorical aggregations
        categorical_cols = self.data.select_dtypes(
            include=['object', 'category']
        ).columns
        
        for col in categorical_cols:
            top_values = self.data[col].value_counts().head(3)
            metrics["categorical_summaries"][col] = {
                "top_categories": top_values.to_dict(),
                "unique_count": int(self.data[col].nunique())
            }
        
        return metrics
