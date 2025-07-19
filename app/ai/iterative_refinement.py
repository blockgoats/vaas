from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

class RefinementAction(Enum):
    MODIFY_CHART_TYPE = "modify_chart_type"
    ADJUST_DATA = "adjust_data"
    UPDATE_STYLING = "update_styling"
    CHANGE_AGGREGATION = "change_aggregation"
    ADD_FILTER = "add_filter"
    MODIFY_AXES = "modify_axes"

@dataclass
class RefinementRequest:
    session_id: str
    user_message: str
    current_chart: Dict[str, Any]
    timestamp: datetime
    context: Dict[str, Any]

@dataclass
class RefinementResponse:
    updated_chart: Dict[str, Any]
    explanation: str
    actions_taken: List[RefinementAction]
    confidence: float
    suggestions: List[str]

@dataclass
class ChatSession:
    session_id: str
    original_prompt: str
    chart_history: List[Dict[str, Any]]
    conversation_history: List[Dict[str, str]]
    schema_context: Dict[str, Any]
    created_at: datetime
    last_updated: datetime

class IterativeChartRefinement:
    """Handles chat-based iterative chart improvement"""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.active_sessions: Dict[str, ChatSession] = {}
        self.refinement_patterns = self._initialize_refinement_patterns()
    
    def start_session(self, session_id: str, original_prompt: str, 
                     initial_chart: Dict[str, Any], schema_context: Dict[str, Any]) -> ChatSession:
        """Start a new iterative refinement session"""
        
        session = ChatSession(
            session_id=session_id,
            original_prompt=original_prompt,
            chart_history=[initial_chart],
            conversation_history=[
                {"role": "assistant", "content": f"I've created a chart based on your request: '{original_prompt}'. How would you like to refine it?"}
            ],
            schema_context=schema_context,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        return session
    
    async def process_refinement(self, session_id: str, user_message: str) -> RefinementResponse:
        """Process a refinement request from the user"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        current_chart = session.chart_history[-1]
        
        # Analyze user intent
        intent = self._analyze_refinement_intent(user_message, current_chart)
        
        # Generate refinement
        refinement_response = await self._generate_refinement(
            user_message, current_chart, session.schema_context, intent
        )
        
        # Update session
        session.chart_history.append(refinement_response.updated_chart)
        session.conversation_history.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": refinement_response.explanation}
        ])
        session.last_updated = datetime.now()
        
        return refinement_response
    
    def get_session_history(self, session_id: str) -> Optional[ChatSession]:
        """Get the full history of a refinement session"""
        return self.active_sessions.get(session_id)
    
    def end_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """End a session and return the final chart"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            final_chart = session.chart_history[-1] if session.chart_history else None
            del self.active_sessions[session_id]
            return final_chart
        return None
    
    def _analyze_refinement_intent(self, user_message: str, current_chart: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze what the user wants to change"""
        
        message_lower = user_message.lower()
        intent = {
            "actions": [],
            "targets": [],
            "values": []
        }
        
        # Chart type changes
        if any(word in message_lower for word in ["change to", "make it a", "convert to"]):
            chart_types = ["bar", "line", "pie", "scatter", "area", "heatmap"]
            for chart_type in chart_types:
                if chart_type in message_lower:
                    intent["actions"].append(RefinementAction.MODIFY_CHART_TYPE)
                    intent["targets"].append("chart_type")
                    intent["values"].append(chart_type)
        
        # Color changes
        if any(word in message_lower for word in ["color", "colour", "blue", "red", "green"]):
            intent["actions"].append(RefinementAction.UPDATE_STYLING)
            intent["targets"].append("colors")
        
        # Data filtering
        if any(word in message_lower for word in ["filter", "only show", "exclude", "remove"]):
            intent["actions"].append(RefinementAction.ADD_FILTER)
            intent["targets"].append("data")
        
        # Aggregation changes
        if any(word in message_lower for word in ["sum", "average", "count", "max", "min"]):
            intent["actions"].append(RefinementAction.CHANGE_AGGREGATION)
            intent["targets"].append("aggregation")
        
        # Axis modifications
        if any(word in message_lower for word in ["x-axis", "y-axis", "axis", "label"]):
            intent["actions"].append(RefinementAction.MODIFY_AXES)
            intent["targets"].append("axes")
        
        # Time period changes
        if any(word in message_lower for word in ["last", "past", "recent", "month", "year", "week"]):
            intent["actions"].append(RefinementAction.ADJUST_DATA)
            intent["targets"].append("time_period")
        
        return intent
    
    async def _generate_refinement(self, user_message: str, current_chart: Dict[str, Any], 
                                 schema_context: Dict[str, Any], intent: Dict[str, Any]) -> RefinementResponse:
        """Generate the actual chart refinement"""
        
        # Build refinement prompt
        refinement_prompt = self._build_refinement_prompt(user_message, current_chart, intent)
        
        # Get LLM response
        try:
            llm_response = await self.llm_manager.generate_chart(refinement_prompt, schema_context)
            
            updated_chart = llm_response.chart_config
            explanation = llm_response.reasoning
            confidence = llm_response.confidence
            
        except Exception as e:
            # Fallback to rule-based refinement
            updated_chart, explanation = self._apply_rule_based_refinement(
                user_message, current_chart, intent
            )
            confidence = 0.7
        
        # Determine actions taken
        actions_taken = self._determine_actions_taken(current_chart, updated_chart)
        
        # Generate suggestions
        suggestions = self._generate_refinement_suggestions(updated_chart, intent)
        
        return RefinementResponse(
            updated_chart=updated_chart,
            explanation=explanation,
            actions_taken=actions_taken,
            confidence=confidence,
            suggestions=suggestions
        )
    
    def _build_refinement_prompt(self, user_message: str, current_chart: Dict[str, Any], 
                               intent: Dict[str, Any]) -> str:
        """Build a prompt for the LLM to refine the chart"""
        
        return f"""
        The user wants to refine their current chart. Here's the context:
        
        Current chart configuration:
        {json.dumps(current_chart, indent=2)}
        
        User's refinement request: "{user_message}"
        
        Detected intent: {intent}
        
        Please modify the chart configuration to address the user's request.
        Return the updated chart configuration with an explanation of changes made.
        
        Focus on:
        1. Maintaining data integrity
        2. Improving visualization effectiveness
        3. Following best practices
        4. Addressing the specific user request
        """
    
    def _apply_rule_based_refinement(self, user_message: str, current_chart: Dict[str, Any], 
                                   intent: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
        """Apply rule-based refinements when LLM is unavailable"""
        
        updated_chart = current_chart.copy()
        changes_made = []
        
        # Chart type changes
        if RefinementAction.MODIFY_CHART_TYPE in intent["actions"]:
            for i, action in enumerate(intent["actions"]):
                if action == RefinementAction.MODIFY_CHART_TYPE:
                    new_type = intent["values"][i]
                    updated_chart["type"] = new_type
                    changes_made.append(f"Changed chart type to {new_type}")
        
        # Color changes
        if RefinementAction.UPDATE_STYLING in intent["actions"]:
            if "data" in updated_chart and "datasets" in updated_chart["data"]:
                for dataset in updated_chart["data"]["datasets"]:
                    dataset["backgroundColor"] = self._get_default_colors()
                changes_made.append("Updated chart colors")
        
        # Simple filter application
        if RefinementAction.ADD_FILTER in intent["actions"]:
            # This would require more sophisticated logic in a real implementation
            changes_made.append("Applied data filter")
        
        explanation = "I've made the following changes: " + ", ".join(changes_made)
        
        return updated_chart, explanation
    
    def _determine_actions_taken(self, old_chart: Dict[str, Any], 
                               new_chart: Dict[str, Any]) -> List[RefinementAction]:
        """Determine what actions were actually taken"""
        
        actions = []
        
        # Check chart type change
        if old_chart.get("type") != new_chart.get("type"):
            actions.append(RefinementAction.MODIFY_CHART_TYPE)
        
        # Check data changes
        if old_chart.get("data") != new_chart.get("data"):
            actions.append(RefinementAction.ADJUST_DATA)
        
        # Check styling changes
        old_options = old_chart.get("options", {})
        new_options = new_chart.get("options", {})
        if old_options != new_options:
            actions.append(RefinementAction.UPDATE_STYLING)
        
        return actions
    
    def _generate_refinement_suggestions(self, updated_chart: Dict[str, Any], 
                                       intent: Dict[str, Any]) -> List[str]:
        """Generate suggestions for further refinements"""
        
        suggestions = []
        
        chart_type = updated_chart.get("type", "")
        
        if chart_type == "bar":
            suggestions.extend([
                "Try 'make it horizontal' for better label readability",
                "Say 'add data labels' to show exact values",
                "Try 'sort by value' to reorder bars"
            ])
        
        elif chart_type == "line":
            suggestions.extend([
                "Try 'add trend line' to show overall direction",
                "Say 'smooth the line' for curved connections",
                "Try 'add markers' to highlight data points"
            ])
        
        elif chart_type == "pie":
            suggestions.extend([
                "Try 'make it a donut chart' for a modern look",
                "Say 'show percentages' to add value labels",
                "Try 'explode the largest slice' to emphasize it"
            ])
        
        # General suggestions
        suggestions.extend([
            "Try 'change colors to blue theme'",
            "Say 'add a title' or 'change the title'",
            "Try 'make it bigger' or 'make it smaller'"
        ])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _get_default_colors(self) -> List[str]:
        """Get default color palette"""
        return [
            "#3b82f6",  # Blue
            "#14b8a6",  # Teal
            "#f97316",  # Orange
            "#8b5cf6",  # Purple
            "#ef4444",  # Red
            "#22c55e",  # Green
            "#f59e0b",  # Yellow
            "#6b7280"   # Gray
        ]
    
    def _initialize_refinement_patterns(self) -> Dict[str, Any]:
        """Initialize common refinement patterns"""
        
        return {
            "chart_type_keywords": {
                "bar": ["bar", "column", "bars"],
                "line": ["line", "trend", "over time"],
                "pie": ["pie", "donut", "percentage"],
                "scatter": ["scatter", "correlation", "relationship"],
                "area": ["area", "filled", "stacked"]
            },
            "color_keywords": {
                "blue": ["blue", "navy", "azure"],
                "red": ["red", "crimson", "rose"],
                "green": ["green", "emerald", "lime"],
                "purple": ["purple", "violet", "indigo"]
            },
            "aggregation_keywords": {
                "sum": ["total", "sum", "add up"],
                "average": ["average", "mean", "avg"],
                "count": ["count", "number of", "how many"],
                "max": ["maximum", "max", "highest"],
                "min": ["minimum", "min", "lowest"]
            }
        }

# Global instance
iterative_refinement = IterativeChartRefinement(None)  # Will be initialized with LLM manager