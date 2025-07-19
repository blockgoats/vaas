from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json

class ValidationLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationIssue:
    level: ValidationLevel
    message: str
    suggestion: Optional[str] = None
    field: Optional[str] = None

@dataclass
class ValidationResult:
    is_valid: bool
    score: float  # 0-1 confidence score
    issues: List[ValidationIssue]
    suggestions: List[str]
    auto_fixes: Dict[str, Any]

class ChartValidator:
    """Validates generated charts for correctness and best practices"""
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
    
    def validate_chart(self, chart_config: Dict[str, Any], original_prompt: str, 
                      schema_context: Dict[str, Any]) -> ValidationResult:
        """Comprehensive chart validation"""
        
        issues = []
        suggestions = []
        auto_fixes = {}
        
        # Validate chart structure
        structure_issues = self._validate_chart_structure(chart_config)
        issues.extend(structure_issues)
        
        # Validate data mapping
        data_issues = self._validate_data_mapping(chart_config, schema_context)
        issues.extend(data_issues)
        
        # Validate chart type appropriateness
        type_issues = self._validate_chart_type(chart_config, original_prompt)
        issues.extend(type_issues)
        
        # Validate accessibility
        accessibility_issues = self._validate_accessibility(chart_config)
        issues.extend(accessibility_issues)
        
        # Validate performance considerations
        performance_issues = self._validate_performance(chart_config)
        issues.extend(performance_issues)
        
        # Generate suggestions and auto-fixes
        suggestions = self._generate_suggestions(issues, chart_config)
        auto_fixes = self._generate_auto_fixes(issues, chart_config)
        
        # Calculate overall score
        error_count = len([i for i in issues if i.level == ValidationLevel.ERROR])
        warning_count = len([i for i in issues if i.level == ValidationLevel.WARNING])
        
        score = max(0.0, 1.0 - (error_count * 0.3) - (warning_count * 0.1))
        is_valid = error_count == 0
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            suggestions=suggestions,
            auto_fixes=auto_fixes
        )
    
    def _validate_chart_structure(self, chart_config: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate basic chart structure and required fields"""
        issues = []
        
        # Check required fields
        required_fields = ["type", "data"]
        for field in required_fields:
            if field not in chart_config:
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Missing required field: {field}",
                    field=field,
                    suggestion=f"Add {field} to chart configuration"
                ))
        
        # Validate chart type
        valid_types = ["bar", "line", "pie", "scatter", "area", "heatmap", "funnel", "treemap"]
        if "type" in chart_config and chart_config["type"] not in valid_types:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Invalid chart type: {chart_config['type']}",
                field="type",
                suggestion=f"Use one of: {', '.join(valid_types)}"
            ))
        
        # Validate data structure
        if "data" in chart_config:
            data = chart_config["data"]
            if not isinstance(data, dict):
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="Chart data must be an object",
                    field="data"
                ))
            elif "datasets" not in data and "labels" not in data:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="Chart data should contain datasets and labels",
                    field="data"
                ))
        
        return issues
    
    def _validate_data_mapping(self, chart_config: Dict[str, Any], 
                             schema_context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate that data mappings make sense"""
        issues = []
        
        if "sql_query" in chart_config:
            sql_query = chart_config["sql_query"]
            
            # Check if referenced tables exist
            available_tables = [table["name"] for table in schema_context.get("tables", [])]
            
            # Simple table name extraction (could be more sophisticated)
            for table_name in available_tables:
                if f"FROM {table_name}" in sql_query.upper() or f"JOIN {table_name}" in sql_query.upper():
                    # Table is referenced, check if it exists
                    if table_name not in [t["name"] for t in schema_context.get("tables", [])]:
                        issues.append(ValidationIssue(
                            level=ValidationLevel.ERROR,
                            message=f"Referenced table '{table_name}' does not exist",
                            field="sql_query",
                            suggestion=f"Use one of the available tables: {', '.join(available_tables)}"
                        ))
        
        return issues
    
    def _validate_chart_type(self, chart_config: Dict[str, Any], 
                           original_prompt: str) -> List[ValidationIssue]:
        """Validate if chart type matches user intent"""
        issues = []
        
        chart_type = chart_config.get("type", "")
        prompt_lower = original_prompt.lower()
        
        # Check for intent-chart type mismatches
        if "over time" in prompt_lower or "trend" in prompt_lower:
            if chart_type not in ["line", "area"]:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="Line or area charts are better for showing trends over time",
                    suggestion="Consider using a line chart for time-series data"
                ))
        
        if "compare" in prompt_lower or "vs" in prompt_lower:
            if chart_type not in ["bar", "column"]:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="Bar charts are typically better for comparisons",
                    suggestion="Consider using a bar chart for comparing values"
                ))
        
        if "distribution" in prompt_lower or "spread" in prompt_lower:
            if chart_type not in ["histogram", "box", "violin"]:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="Histogram or box plots are better for showing distributions",
                    suggestion="Consider using a histogram for distribution analysis"
                ))
        
        if "percentage" in prompt_lower or "proportion" in prompt_lower:
            if chart_type not in ["pie", "donut", "treemap"]:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="Pie charts or treemaps are better for showing proportions",
                    suggestion="Consider using a pie chart for percentage breakdowns"
                ))
        
        return issues
    
    def _validate_accessibility(self, chart_config: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate chart accessibility features"""
        issues = []
        
        # Check for color accessibility
        if "data" in chart_config and "datasets" in chart_config["data"]:
            for dataset in chart_config["data"]["datasets"]:
                if "backgroundColor" in dataset:
                    colors = dataset["backgroundColor"]
                    if isinstance(colors, list) and len(colors) > 1:
                        # Check for color contrast (simplified)
                        if self._has_poor_color_contrast(colors):
                            issues.append(ValidationIssue(
                                level=ValidationLevel.WARNING,
                                message="Color palette may not be accessible to colorblind users",
                                suggestion="Use colorblind-friendly color palettes"
                            ))
        
        # Check for alt text
        if "options" not in chart_config or "plugins" not in chart_config["options"]:
            issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                message="Consider adding alt text for screen readers",
                suggestion="Add accessibility options to chart configuration"
            ))
        
        return issues
    
    def _validate_performance(self, chart_config: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate performance considerations"""
        issues = []
        
        # Check data size
        if "data" in chart_config and "datasets" in chart_config["data"]:
            for dataset in chart_config["data"]["datasets"]:
                if "data" in dataset and isinstance(dataset["data"], list):
                    data_points = len(dataset["data"])
                    if data_points > 1000:
                        issues.append(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            message=f"Large dataset ({data_points} points) may impact performance",
                            suggestion="Consider data aggregation or pagination"
                        ))
        
        # Check for expensive operations
        if "options" in chart_config and "animation" in chart_config["options"]:
            if chart_config["options"]["animation"].get("duration", 0) > 2000:
                issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    message="Long animation duration may impact user experience",
                    suggestion="Consider shorter animation duration (< 1000ms)"
                ))
        
        return issues
    
    def _has_poor_color_contrast(self, colors: List[str]) -> bool:
        """Simple check for color contrast issues"""
        # This is a simplified check - in production, use proper color contrast algorithms
        similar_colors = [
            ["#ff0000", "#ff4444"],  # Similar reds
            ["#00ff00", "#44ff44"],  # Similar greens
            ["#0000ff", "#4444ff"],  # Similar blues
        ]
        
        for color_group in similar_colors:
            if any(color in colors for color in color_group):
                return True
        
        return False
    
    def _generate_suggestions(self, issues: List[ValidationIssue], 
                            chart_config: Dict[str, Any]) -> List[str]:
        """Generate actionable suggestions based on validation issues"""
        suggestions = []
        
        error_count = len([i for i in issues if i.level == ValidationLevel.ERROR])
        warning_count = len([i for i in issues if i.level == ValidationLevel.WARNING])
        
        if error_count > 0:
            suggestions.append("Fix critical errors before proceeding with chart generation")
        
        if warning_count > 0:
            suggestions.append("Consider addressing warnings to improve chart quality")
        
        # Chart-specific suggestions
        chart_type = chart_config.get("type", "")
        
        if chart_type == "pie":
            suggestions.append("Limit pie chart to 5-7 categories for better readability")
        
        if chart_type == "line":
            suggestions.append("Ensure time-series data is properly sorted by date")
        
        if chart_type == "bar":
            suggestions.append("Consider horizontal bars for long category names")
        
        return suggestions
    
    def _generate_auto_fixes(self, issues: List[ValidationIssue], 
                           chart_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate automatic fixes for common issues"""
        auto_fixes = {}
        
        for issue in issues:
            if issue.field == "type" and "Invalid chart type" in issue.message:
                auto_fixes["type"] = "bar"  # Default fallback
            
            if issue.field == "data" and "Chart data must be an object" in issue.message:
                auto_fixes["data"] = {"labels": [], "datasets": []}
            
            if "accessibility" in issue.message.lower():
                auto_fixes["options"] = {
                    **chart_config.get("options", {}),
                    "plugins": {
                        **chart_config.get("options", {}).get("plugins", {}),
                        "accessibility": {
                            "enabled": True,
                            "description": "Auto-generated chart description"
                        }
                    }
                }
        
        return auto_fixes
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules configuration"""
        return {
            "required_fields": ["type", "data"],
            "valid_chart_types": ["bar", "line", "pie", "scatter", "area", "heatmap"],
            "max_data_points": 1000,
            "max_animation_duration": 2000,
            "accessibility_required": True
        }