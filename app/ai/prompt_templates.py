from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class PromptCategory(Enum):
    SALES = "sales"
    MARKETING = "marketing"
    FINANCE = "finance"
    OPERATIONS = "operations"
    HR = "hr"
    PRODUCT = "product"
    CUSTOMER = "customer"

@dataclass
class PromptTemplate:
    id: str
    name: str
    description: str
    category: PromptCategory
    template: str
    variables: List[str]
    example_output: str
    chart_types: List[str]

class PromptTemplateManager:
    """Manages pre-built prompt templates for common use cases"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def get_templates_by_category(self, category: PromptCategory) -> List[PromptTemplate]:
        """Get all templates for a specific category"""
        return [t for t in self.templates if t.category == category]
    
    def get_template_by_id(self, template_id: str) -> PromptTemplate:
        """Get a specific template by ID"""
        for template in self.templates:
            if template.id == template_id:
                return template
        raise ValueError(f"Template {template_id} not found")
    
    def render_template(self, template_id: str, variables: Dict[str, str]) -> str:
        """Render a template with provided variables"""
        template = self.get_template_by_id(template_id)
        
        rendered = template.template
        for var_name, var_value in variables.items():
            rendered = rendered.replace(f"{{{var_name}}}", var_value)
        
        return rendered
    
    def suggest_templates(self, user_input: str) -> List[PromptTemplate]:
        """Suggest relevant templates based on user input"""
        user_lower = user_input.lower()
        suggestions = []
        
        for template in self.templates:
            # Check if any keywords match
            template_keywords = template.description.lower().split()
            if any(keyword in user_lower for keyword in template_keywords):
                suggestions.append(template)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _initialize_templates(self) -> List[PromptTemplate]:
        """Initialize all prompt templates"""
        
        return [
            # Sales Templates
            PromptTemplate(
                id="sales_performance_monthly",
                name="Monthly Sales Performance",
                description="Track monthly sales performance across regions",
                category=PromptCategory.SALES,
                template="Show me {metric} by {dimension} for the last {time_period} months",
                variables=["metric", "dimension", "time_period"],
                example_output="Show me total sales by region for the last 12 months",
                chart_types=["bar", "line"]
            ),
            
            PromptTemplate(
                id="sales_funnel_conversion",
                name="Sales Funnel Analysis",
                description="Analyze conversion rates through sales funnel stages",
                category=PromptCategory.SALES,
                template="Create a funnel chart showing conversion from {stage1} to {stage2} to {stage3}",
                variables=["stage1", "stage2", "stage3"],
                example_output="Create a funnel chart showing conversion from leads to opportunities to closed deals",
                chart_types=["funnel", "bar"]
            ),
            
            PromptTemplate(
                id="top_performing_products",
                name="Top Performing Products",
                description="Identify best-selling products by revenue or quantity",
                category=PromptCategory.SALES,
                template="Show me the top {number} products by {metric} in {time_period}",
                variables=["number", "metric", "time_period"],
                example_output="Show me the top 10 products by revenue in Q4 2023",
                chart_types=["bar", "pie"]
            ),
            
            # Marketing Templates
            PromptTemplate(
                id="campaign_performance",
                name="Marketing Campaign Performance",
                description="Compare performance metrics across marketing campaigns",
                category=PromptCategory.MARKETING,
                template="Compare {metric} across {campaigns} campaigns for {time_period}",
                variables=["metric", "campaigns", "time_period"],
                example_output="Compare click-through rates across email, social, and PPC campaigns for last quarter",
                chart_types=["bar", "line"]
            ),
            
            PromptTemplate(
                id="customer_acquisition_cost",
                name="Customer Acquisition Cost Trends",
                description="Track customer acquisition costs over time by channel",
                category=PromptCategory.MARKETING,
                template="Show customer acquisition cost trends by {channel} over {time_period}",
                variables=["channel", "time_period"],
                example_output="Show customer acquisition cost trends by marketing channel over the last year",
                chart_types=["line", "area"]
            ),
            
            PromptTemplate(
                id="website_traffic_sources",
                name="Website Traffic Sources",
                description="Analyze website traffic by source and medium",
                category=PromptCategory.MARKETING,
                template="Break down website traffic by {dimension} for {time_period}",
                variables=["dimension", "time_period"],
                example_output="Break down website traffic by source/medium for the last 6 months",
                chart_types=["pie", "treemap"]
            ),
            
            # Finance Templates
            PromptTemplate(
                id="revenue_growth",
                name="Revenue Growth Analysis",
                description="Track revenue growth trends over time",
                category=PromptCategory.FINANCE,
                template="Show {revenue_type} growth {comparison} over {time_period}",
                variables=["revenue_type", "comparison", "time_period"],
                example_output="Show monthly recurring revenue growth year-over-year over the last 24 months",
                chart_types=["line", "area"]
            ),
            
            PromptTemplate(
                id="expense_breakdown",
                name="Expense Category Breakdown",
                description="Analyze expenses by category and department",
                category=PromptCategory.FINANCE,
                template="Break down {expense_type} expenses by {dimension} for {time_period}",
                variables=["expense_type", "dimension", "time_period"],
                example_output="Break down operational expenses by department for Q3 2023",
                chart_types=["pie", "bar"]
            ),
            
            PromptTemplate(
                id="profit_margin_trends",
                name="Profit Margin Analysis",
                description="Track profit margins across products or time periods",
                category=PromptCategory.FINANCE,
                template="Show {margin_type} margins by {dimension} over {time_period}",
                variables=["margin_type", "dimension", "time_period"],
                example_output="Show gross profit margins by product category over the last year",
                chart_types=["line", "bar"]
            ),
            
            # Operations Templates
            PromptTemplate(
                id="inventory_levels",
                name="Inventory Level Monitoring",
                description="Track inventory levels and turnover rates",
                category=PromptCategory.OPERATIONS,
                template="Show {inventory_metric} for {product_category} over {time_period}",
                variables=["inventory_metric", "product_category", "time_period"],
                example_output="Show inventory turnover rates for electronics category over the last quarter",
                chart_types=["line", "bar"]
            ),
            
            PromptTemplate(
                id="production_efficiency",
                name="Production Efficiency Metrics",
                description="Monitor production efficiency and quality metrics",
                category=PromptCategory.OPERATIONS,
                template="Track {efficiency_metric} by {production_line} for {time_period}",
                variables=["efficiency_metric", "production_line", "time_period"],
                example_output="Track defect rates by production line for the last month",
                chart_types=["line", "heatmap"]
            ),
            
            PromptTemplate(
                id="supply_chain_performance",
                name="Supply Chain Performance",
                description="Analyze supplier performance and delivery metrics",
                category=PromptCategory.OPERATIONS,
                template="Show {performance_metric} by {supplier} for {time_period}",
                variables=["performance_metric", "supplier", "time_period"],
                example_output="Show on-time delivery rates by supplier for the last 6 months",
                chart_types=["bar", "heatmap"]
            ),
            
            # HR Templates
            PromptTemplate(
                id="employee_turnover",
                name="Employee Turnover Analysis",
                description="Track employee turnover rates by department",
                category=PromptCategory.HR,
                template="Show {turnover_metric} by {department} for {time_period}",
                variables=["turnover_metric", "department", "time_period"],
                example_output="Show monthly turnover rates by department for the last year",
                chart_types=["line", "bar"]
            ),
            
            PromptTemplate(
                id="hiring_pipeline",
                name="Hiring Pipeline Analysis",
                description="Analyze recruitment funnel and time-to-hire metrics",
                category=PromptCategory.HR,
                template="Show {hiring_metric} for {position_type} over {time_period}",
                variables=["hiring_metric", "position_type", "time_period"],
                example_output="Show time-to-hire for engineering positions over the last quarter",
                chart_types=["funnel", "line"]
            ),
            
            PromptTemplate(
                id="employee_satisfaction",
                name="Employee Satisfaction Trends",
                description="Track employee satisfaction scores and engagement",
                category=PromptCategory.HR,
                template="Show {satisfaction_metric} trends by {dimension} over {time_period}",
                variables=["satisfaction_metric", "dimension", "time_period"],
                example_output="Show employee satisfaction score trends by department over the last year",
                chart_types=["line", "heatmap"]
            ),
            
            # Product Templates
            PromptTemplate(
                id="feature_usage",
                name="Product Feature Usage",
                description="Analyze which product features are most used",
                category=PromptCategory.PRODUCT,
                template="Show {usage_metric} for {feature_set} over {time_period}",
                variables=["usage_metric", "feature_set", "time_period"],
                example_output="Show daily active usage for core features over the last month",
                chart_types=["bar", "heatmap"]
            ),
            
            PromptTemplate(
                id="user_engagement",
                name="User Engagement Metrics",
                description="Track user engagement and activity patterns",
                category=PromptCategory.PRODUCT,
                template="Show {engagement_metric} by {user_segment} over {time_period}",
                variables=["engagement_metric", "user_segment", "time_period"],
                example_output="Show session duration by user cohort over the last 3 months",
                chart_types=["line", "area"]
            ),
            
            PromptTemplate(
                id="product_adoption",
                name="Product Adoption Funnel",
                description="Analyze user onboarding and feature adoption",
                category=PromptCategory.PRODUCT,
                template="Create adoption funnel from {step1} to {step2} to {step3}",
                variables=["step1", "step2", "step3"],
                example_output="Create adoption funnel from signup to first action to daily active user",
                chart_types=["funnel", "bar"]
            ),
            
            # Customer Templates
            PromptTemplate(
                id="customer_retention",
                name="Customer Retention Analysis",
                description="Track customer retention and churn rates",
                category=PromptCategory.CUSTOMER,
                template="Show {retention_metric} by {customer_segment} over {time_period}",
                variables=["retention_metric", "customer_segment", "time_period"],
                example_output="Show monthly retention rates by customer tier over the last year",
                chart_types=["line", "heatmap"]
            ),
            
            PromptTemplate(
                id="customer_lifetime_value",
                name="Customer Lifetime Value",
                description="Analyze customer lifetime value by segment",
                category=PromptCategory.CUSTOMER,
                template="Show {clv_metric} by {customer_dimension} for {time_period}",
                variables=["clv_metric", "customer_dimension", "time_period"],
                example_output="Show average customer lifetime value by acquisition channel for 2023",
                chart_types=["bar", "scatter"]
            ),
            
            PromptTemplate(
                id="support_ticket_analysis",
                name="Customer Support Analysis",
                description="Analyze support ticket volume and resolution times",
                category=PromptCategory.CUSTOMER,
                template="Show {support_metric} by {ticket_category} over {time_period}",
                variables=["support_metric", "ticket_category", "time_period"],
                example_output="Show average resolution time by ticket priority over the last quarter",
                chart_types=["bar", "line"]
            )
        ]

# Global instance
prompt_template_manager = PromptTemplateManager()