from typing import Dict, Any, List, Optional
import pandas as pd
from dataclasses import dataclass
from enum import Enum

class DataType(Enum):
    CATEGORICAL = "categorical"
    NUMERICAL = "numerical"
    TEMPORAL = "temporal"
    GEOGRAPHICAL = "geographical"
    BOOLEAN = "boolean"

class ChartType(Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HEATMAP = "heatmap"
    FUNNEL = "funnel"
    TREEMAP = "treemap"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box"
    VIOLIN = "violin"
    SANKEY = "sankey"
    GAUGE = "gauge"
    WATERFALL = "waterfall"

@dataclass
class ColumnInfo:
    name: str
    data_type: DataType
    unique_values: int
    null_percentage: float
    sample_values: List[Any]
    is_primary_key: bool = False
    is_foreign_key: bool = False

@dataclass
class ChartRecommendation:
    chart_type: ChartType
    confidence: float
    reasoning: str
    suggested_config: Dict[str, Any]
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    color_by: Optional[str] = None
    size_by: Optional[str] = None

class ChartIntelligence:
    """AI-powered chart type recommendation engine"""
    
    def __init__(self):
        self.chart_rules = self._initialize_chart_rules()
    
    def analyze_data_context(self, schema_info: Dict[str, Any], sample_data: Optional[pd.DataFrame] = None) -> Dict[str, ColumnInfo]:
        """Analyze database schema and sample data to understand data characteristics"""
        columns_info = {}
        
        for table in schema_info.get("tables", []):
            for column in table.get("columns", []):
                col_info = self._analyze_column(column, sample_data)
                columns_info[f"{table['name']}.{column['name']}"] = col_info
        
        return columns_info
    
    def recommend_charts(self, prompt: str, columns_info: Dict[str, ColumnInfo]) -> List[ChartRecommendation]:
        """Recommend optimal chart types based on prompt and data characteristics"""
        
        # Parse intent from prompt
        intent = self._parse_user_intent(prompt)
        
        # Identify relevant columns
        relevant_columns = self._identify_relevant_columns(prompt, columns_info)
        
        # Generate recommendations
        recommendations = []
        
        for chart_type in ChartType:
            confidence = self._calculate_chart_confidence(
                chart_type, intent, relevant_columns, columns_info
            )
            
            if confidence > 0.3:  # Only include viable options
                recommendation = ChartRecommendation(
                    chart_type=chart_type,
                    confidence=confidence,
                    reasoning=self._generate_reasoning(chart_type, intent, relevant_columns),
                    suggested_config=self._generate_chart_config(chart_type, relevant_columns),
                    **self._suggest_axis_mappings(chart_type, relevant_columns)
                )
                recommendations.append(recommendation)
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        return recommendations[:5]  # Return top 5
    
    def validate_chart_choice(self, chart_type: ChartType, columns: List[str], columns_info: Dict[str, ColumnInfo]) -> Dict[str, Any]:
        """Validate if chosen chart type is appropriate for the data"""
        
        issues = []
        suggestions = []
        
        # Check data type compatibility
        if chart_type in [ChartType.LINE, ChartType.AREA]:
            if not any(columns_info[col].data_type == DataType.TEMPORAL for col in columns):
                issues.append("Line/Area charts work best with time-series data")
                suggestions.append("Consider using a bar chart instead")
        
        elif chart_type == ChartType.PIE:
            categorical_cols = [col for col in columns if columns_info[col].data_type == DataType.CATEGORICAL]
            if not categorical_cols:
                issues.append("Pie charts require categorical data")
                suggestions.append("Use a bar chart for numerical comparisons")
            
            if len(categorical_cols) > 1:
                issues.append("Pie charts work best with a single categorical dimension")
                suggestions.append("Consider a stacked bar chart for multiple categories")
        
        elif chart_type == ChartType.SCATTER:
            numerical_cols = [col for col in columns if columns_info[col].data_type == DataType.NUMERICAL]
            if len(numerical_cols) < 2:
                issues.append("Scatter plots require at least two numerical variables")
                suggestions.append("Use a histogram for single variable analysis")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "confidence": 1.0 - (len(issues) * 0.2)
        }
    
    def _analyze_column(self, column: Dict[str, Any], sample_data: Optional[pd.DataFrame]) -> ColumnInfo:
        """Analyze individual column characteristics"""
        
        # Determine data type from SQL type
        sql_type = column.get("type", "").lower()
        data_type = self._infer_data_type(sql_type, column.get("name", ""))
        
        # Default values
        unique_values = 0
        null_percentage = 0.0
        sample_values = []
        
        # If we have sample data, analyze it
        if sample_data is not None and column["name"] in sample_data.columns:
            col_data = sample_data[column["name"]]
            unique_values = col_data.nunique()
            null_percentage = col_data.isnull().sum() / len(col_data)
            sample_values = col_data.dropna().head(5).tolist()
        
        return ColumnInfo(
            name=column["name"],
            data_type=data_type,
            unique_values=unique_values,
            null_percentage=null_percentage,
            sample_values=sample_values,
            is_primary_key=column.get("is_primary_key", False),
            is_foreign_key=column.get("is_foreign_key", False)
        )
    
    def _infer_data_type(self, sql_type: str, column_name: str) -> DataType:
        """Infer semantic data type from SQL type and column name"""
        
        # Temporal patterns
        if any(keyword in sql_type for keyword in ["timestamp", "datetime", "date", "time"]):
            return DataType.TEMPORAL
        
        if any(keyword in column_name.lower() for keyword in ["date", "time", "created", "updated"]):
            return DataType.TEMPORAL
        
        # Numerical patterns
        if any(keyword in sql_type for keyword in ["int", "float", "decimal", "numeric", "double"]):
            return DataType.NUMERICAL
        
        # Boolean patterns
        if "bool" in sql_type or column_name.lower() in ["active", "enabled", "is_", "has_"]:
            return DataType.BOOLEAN
        
        # Geographical patterns
        if any(keyword in column_name.lower() for keyword in ["lat", "lng", "longitude", "latitude", "country", "state", "city", "zip"]):
            return DataType.GEOGRAPHICAL
        
        # Default to categorical
        return DataType.CATEGORICAL
    
    def _parse_user_intent(self, prompt: str) -> Dict[str, Any]:
        """Parse user intent from natural language prompt"""
        
        prompt_lower = prompt.lower()
        
        intent = {
            "comparison": any(word in prompt_lower for word in ["compare", "vs", "versus", "difference", "between"]),
            "trend": any(word in prompt_lower for word in ["trend", "over time", "timeline", "progression", "growth"]),
            "distribution": any(word in prompt_lower for word in ["distribution", "spread", "histogram", "frequency"]),
            "correlation": any(word in prompt_lower for word in ["correlation", "relationship", "scatter", "vs"]),
            "composition": any(word in prompt_lower for word in ["breakdown", "composition", "pie", "percentage", "share"]),
            "ranking": any(word in prompt_lower for word in ["top", "bottom", "rank", "highest", "lowest", "best", "worst"]),
            "geographical": any(word in prompt_lower for word in ["map", "region", "country", "state", "location", "geographic"])
        }
        
        return intent
    
    def _identify_relevant_columns(self, prompt: str, columns_info: Dict[str, ColumnInfo]) -> List[str]:
        """Identify columns mentioned or relevant to the prompt"""
        
        prompt_lower = prompt.lower()
        relevant_columns = []
        
        for col_name, col_info in columns_info.items():
            # Direct mention
            if col_info.name.lower() in prompt_lower:
                relevant_columns.append(col_name)
                continue
            
            # Semantic matching
            if any(keyword in prompt_lower for keyword in ["sales", "revenue", "amount", "price"]):
                if any(keyword in col_info.name.lower() for keyword in ["sales", "revenue", "amount", "price", "total"]):
                    relevant_columns.append(col_name)
            
            if any(keyword in prompt_lower for keyword in ["user", "customer", "client"]):
                if any(keyword in col_info.name.lower() for keyword in ["user", "customer", "client", "account"]):
                    relevant_columns.append(col_name)
            
            if any(keyword in prompt_lower for keyword in ["time", "date", "month", "year"]):
                if col_info.data_type == DataType.TEMPORAL:
                    relevant_columns.append(col_name)
        
        return relevant_columns
    
    def _calculate_chart_confidence(self, chart_type: ChartType, intent: Dict[str, Any], 
                                  relevant_columns: List[str], columns_info: Dict[str, ColumnInfo]) -> float:
        """Calculate confidence score for a chart type given the context"""
        
        if not relevant_columns:
            return 0.0
        
        confidence = 0.0
        
        # Get data types of relevant columns
        data_types = [columns_info[col].data_type for col in relevant_columns]
        
        # Chart type specific scoring
        if chart_type == ChartType.BAR:
            confidence += 0.8 if intent["comparison"] else 0.3
            confidence += 0.6 if DataType.CATEGORICAL in data_types else 0.0
            confidence += 0.4 if DataType.NUMERICAL in data_types else 0.0
        
        elif chart_type == ChartType.LINE:
            confidence += 0.9 if intent["trend"] else 0.2
            confidence += 0.8 if DataType.TEMPORAL in data_types else 0.0
            confidence += 0.4 if DataType.NUMERICAL in data_types else 0.0
        
        elif chart_type == ChartType.PIE:
            confidence += 0.8 if intent["composition"] else 0.2
            confidence += 0.7 if len([dt for dt in data_types if dt == DataType.CATEGORICAL]) == 1 else 0.0
            confidence -= 0.3 if len(relevant_columns) > 2 else 0.0
        
        elif chart_type == ChartType.SCATTER:
            confidence += 0.9 if intent["correlation"] else 0.3
            confidence += 0.8 if len([dt for dt in data_types if dt == DataType.NUMERICAL]) >= 2 else 0.0
        
        elif chart_type == ChartType.HEATMAP:
            confidence += 0.7 if intent["correlation"] else 0.2
            confidence += 0.6 if len(data_types) >= 2 else 0.0
        
        elif chart_type == ChartType.HISTOGRAM:
            confidence += 0.9 if intent["distribution"] else 0.3
            confidence += 0.8 if DataType.NUMERICAL in data_types else 0.0
            confidence -= 0.4 if len(relevant_columns) > 1 else 0.0
        
        return min(confidence, 1.0)
    
    def _generate_reasoning(self, chart_type: ChartType, intent: Dict[str, Any], relevant_columns: List[str]) -> str:
        """Generate human-readable reasoning for chart recommendation"""
        
        reasons = []
        
        if chart_type == ChartType.BAR and intent["comparison"]:
            reasons.append("Bar charts excel at comparing values across categories")
        
        if chart_type == ChartType.LINE and intent["trend"]:
            reasons.append("Line charts are ideal for showing trends over time")
        
        if chart_type == ChartType.PIE and intent["composition"]:
            reasons.append("Pie charts effectively show part-to-whole relationships")
        
        if chart_type == ChartType.SCATTER and intent["correlation"]:
            reasons.append("Scatter plots reveal relationships between numerical variables")
        
        if not reasons:
            reasons.append(f"{chart_type.value.title()} chart is suitable for this data type")
        
        return ". ".join(reasons)
    
    def _generate_chart_config(self, chart_type: ChartType, relevant_columns: List[str]) -> Dict[str, Any]:
        """Generate basic chart configuration"""
        
        config = {
            "type": chart_type.value,
            "responsive": True,
            "plugins": {
                "legend": {"display": True},
                "tooltip": {"enabled": True}
            }
        }
        
        if chart_type in [ChartType.BAR, ChartType.LINE]:
            config["scales"] = {
                "x": {"display": True},
                "y": {"display": True}
            }
        
        return config
    
    def _suggest_axis_mappings(self, chart_type: ChartType, relevant_columns: List[str]) -> Dict[str, Optional[str]]:
        """Suggest which columns should map to which axes"""
        
        if len(relevant_columns) < 2:
            return {"x_axis": None, "y_axis": None, "color_by": None, "size_by": None}
        
        # Simple heuristic - can be made more sophisticated
        return {
            "x_axis": relevant_columns[0] if relevant_columns else None,
            "y_axis": relevant_columns[1] if len(relevant_columns) > 1 else None,
            "color_by": relevant_columns[2] if len(relevant_columns) > 2 else None,
            "size_by": relevant_columns[3] if len(relevant_columns) > 3 else None
        }
    
    def _initialize_chart_rules(self) -> Dict[str, Any]:
        """Initialize chart recommendation rules"""
        
        return {
            "data_type_compatibility": {
                ChartType.BAR: [DataType.CATEGORICAL, DataType.NUMERICAL],
                ChartType.LINE: [DataType.TEMPORAL, DataType.NUMERICAL],
                ChartType.PIE: [DataType.CATEGORICAL],
                ChartType.SCATTER: [DataType.NUMERICAL],
                ChartType.HEATMAP: [DataType.CATEGORICAL, DataType.NUMERICAL],
                ChartType.HISTOGRAM: [DataType.NUMERICAL]
            },
            "intent_mapping": {
                "comparison": [ChartType.BAR, ChartType.HEATMAP],
                "trend": [ChartType.LINE, ChartType.AREA],
                "distribution": [ChartType.HISTOGRAM, ChartType.BOX_PLOT],
                "correlation": [ChartType.SCATTER, ChartType.HEATMAP],
                "composition": [ChartType.PIE, ChartType.TREEMAP],
                "ranking": [ChartType.BAR, ChartType.FUNNEL]
            }
        }