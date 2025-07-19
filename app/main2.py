



from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import jwt
from datetime import datetime, timedelta
import os
from app.ai.llm_providers import create_llm_manager
from app.ai.prompt_templates import prompt_template_manager, PromptCategory
from app.ai.chart_intelligence import ChartIntelligence
from app.ai.iterative_refinement import IterativeChartRefinement
from app.ai.batch_generation import BatchChartGenerator, BatchTemplates

app = FastAPI(title="BI Platform API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI components
llm_manager = create_llm_manager()
chart_intelligence = ChartIntelligence()
iterative_refinement = IterativeChartRefinement(llm_manager)
batch_generator = BatchChartGenerator(llm_manager)

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable

# Models
class User(BaseModel):
    id: str
    email: str
    name: str
    role: str
    workspace_id: str

class Workspace(BaseModel):
    id: str
    name: str
    description: str
    created_at: str
    member_count: int
    status: str

class DataSource(BaseModel):
    id: str
    name: str
    type: str
    host: str
    port: int
    database: str
    status: str
    created_at: str

class Chart(BaseModel):
    id: str
    name: str
    type: str
    config: dict
    workspace_id: str
    created_by: str
    created_at: str
    is_ai_generated: bool

class AIChartRequest(BaseModel):
    prompt: str
    workspace_id: str
    data_source_id: Optional[str] = None
    use_template: Optional[str] = None
    chart_type_hint: Optional[str] = None

class ChartRefinementRequest(BaseModel):
    session_id: str
    user_message: str

class BatchChartRequest(BaseModel):
    workspace_id: str
    chart_requests: List[Dict[str, Any]]
    template_name: Optional[str] = None

class PromptTemplateRequest(BaseModel):
    template_id: str
    variables: Dict[str, str]

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

# Mock data
mock_users = [
    User(
        id="1",
        email="admin@example.com",
        name="Admin User",
        role="admin",
        workspace_id="ws-1"
    )
]

mock_workspaces = [
    Workspace(
        id="ws-1",
        name="Analytics Team",
        description="Main analytics workspace",
        created_at="2024-01-15",
        member_count=12,
        status="active"
    )
]

# Authentication
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return next((user for user in mock_users if user.id == user_id), None)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    # Mock authentication
    if request.email == "admin@example.com" and request.password == "admin":
        user = mock_users[0]
        token_data = {"sub": user.id, "exp": datetime.utcnow() + timedelta(hours=24)}
        token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
        return TokenResponse(access_token=token, token_type="bearer", user=user)
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/users/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/api/workspaces", response_model=List[Workspace])
async def get_workspaces(current_user: User = Depends(get_current_user)):
    return mock_workspaces

@app.post("/api/workspaces", response_model=Workspace)
async def create_workspace(workspace: Workspace, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    mock_workspaces.append(workspace)
    return workspace

@app.get("/api/data-sources")
async def get_data_sources(current_user: User = Depends(get_current_user)):
    # Mock data sources
    return [
        {
            "id": "ds-1",
            "name": "Production PostgreSQL",
            "type": "PostgreSQL",
            "host": "prod-db.company.com",
            "status": "connected",
            "created_at": "2024-01-15"
        }
    ]

@app.post("/api/data-sources")
async def create_data_source(data_source: dict, current_user: User = Depends(get_current_user)):
    # In real implementation, would validate connection and store in database
    return {"id": "ds-new", "status": "created", **data_source}

@app.post("/api/charts/ai-generate")
async def generate_ai_chart(request: AIChartRequest, current_user: User = Depends(get_current_user)):
    """
    Enhanced AI chart generation with multi-LLM support and intelligence
    """
    
    try:
        # Handle template usage
        prompt = request.prompt
        if request.use_template:
            # This would render a template with variables in a real implementation
            pass
        
        # Get schema context for the data source
        schema_context = {"tables": []}  # Would fetch from database in production
        
        # Generate chart using AI
        llm_response = await llm_manager.generate_chart(prompt, schema_context)
        
        # Get chart recommendations
        columns_info = chart_intelligence.analyze_data_context(schema_context)
        recommendations = chart_intelligence.recommend_charts(prompt, columns_info)
        
        return {
            "chart": {
                "id": f"chart-{datetime.now().timestamp()}",
                "name": llm_response.title,
                "type": llm_response.chart_type,
                "config": llm_response.chart_config,
                "sql_query": llm_response.sql_query,
                "workspace_id": request.workspace_id,
                "created_by": current_user.id,
                "created_at": datetime.now().isoformat(),
                "is_ai_generated": True,
                "confidence": llm_response.confidence,
                "reasoning": llm_response.reasoning
            },
            "recommendations": [
                {
                    "chart_type": rec.chart_type.value,
                    "confidence": rec.confidence,
                    "reasoning": rec.reasoning
                } for rec in recommendations[:3]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/charts/suggest-types")
async def suggest_chart_types(data_description: str, current_user: User = Depends(get_current_user)):
    """Get chart type suggestions based on data description"""
    try:
        suggestions = await llm_manager.suggest_chart_type(data_description)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/charts/validate")
async def validate_chart(chart_config: Dict[str, Any], original_prompt: str, 
                        current_user: User = Depends(get_current_user)):
    """Validate a chart configuration"""
    try:
        validation_result = await llm_manager.validate_chart(chart_config, original_prompt)
        return {"validation": validation_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/charts/refine")
async def refine_chart(request: ChartRefinementRequest, current_user: User = Depends(get_current_user)):
    """Iteratively refine a chart based on user feedback"""
    try:
        refinement_response = await iterative_refinement.process_refinement(
            request.session_id, request.user_message
        )
        return {"refinement": refinement_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/charts/start-refinement-session")
async def start_refinement_session(chart_config: Dict[str, Any], original_prompt: str,
                                 current_user: User = Depends(get_current_user)):
    """Start a new iterative refinement session"""
    try:
        session_id = f"session_{current_user.id}_{datetime.now().timestamp()}"
        schema_context = {"tables": []}  # Would fetch from database
        
        session = iterative_refinement.start_session(
            session_id, original_prompt, chart_config, schema_context
        )
        
        return {"session_id": session_id, "session": session}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/charts/batch-generate")
async def batch_generate_charts(request: BatchChartRequest, current_user: User = Depends(get_current_user)):
    """Generate multiple charts in batch"""
    try:
        chart_requests = request.chart_requests
        
        # Use template if specified
        if request.template_name:
            if request.template_name == "executive":
                chart_requests = BatchTemplates.executive_dashboard()
            elif request.template_name == "marketing":
                chart_requests = BatchTemplates.marketing_dashboard()
            elif request.template_name == "operations":
                chart_requests = BatchTemplates.operations_dashboard()
        
        job_id = batch_generator.create_batch_job(
            request.workspace_id, current_user.id, chart_requests
        )
        
        return {"job_id": job_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/charts/batch-status/{job_id}")
async def get_batch_status(job_id: str, current_user: User = Depends(get_current_user)):
    """Get status of a batch generation job"""
    try:
        job = batch_generator.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {"job": job}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prompt-templates")
async def get_prompt_templates(category: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """Get available prompt templates"""
    try:
        if category:
            category_enum = PromptCategory(category)
            templates = prompt_template_manager.get_templates_by_category(category_enum)
        else:
            templates = prompt_template_manager.templates
        
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prompt-templates/render")
async def render_prompt_template(request: PromptTemplateRequest, current_user: User = Depends(get_current_user)):
    """Render a prompt template with variables"""
    try:
        rendered_prompt = prompt_template_manager.render_template(
            request.template_id, request.variables
        )
        return {"rendered_prompt": rendered_prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prompt-templates/suggest")
async def suggest_prompt_templates(user_input: str, current_user: User = Depends(get_current_user)):
    """Suggest relevant prompt templates based on user input"""
    try:
        suggestions = prompt_template_manager.suggest_templates(user_input)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/providers")
async def get_ai_providers(current_user: User = Depends(get_current_user)):
    """Get available AI providers and their status"""
    try:
        providers = {
            "available_providers": list(llm_manager.providers.keys()),
            "primary_provider": llm_manager.primary_provider,
            "fallback_order": llm_manager.fallback_order
        }
        return providers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoint for backward compatibility
@app.post("/api/charts/ai-generate-legacy")
async def generate_ai_chart_legacy(request: AIChartRequest, current_user: User = Depends(get_current_user)):
    """
    Legacy AI chart generation endpoint (original implementation)
    """
    
    # Mock chart configuration
    mock_config = {
        "type": "bar",
        "data": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
            "datasets": [{
                "label": "Generated Data",
                "data": [12, 19, 3, 5, 2],
                "backgroundColor": "rgba(59, 130, 246, 0.5)"
            }]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": f"AI Generated Chart: {request.prompt}"
                }
            }
        }
    }
    
    chart = Chart(
        id=f"chart-{datetime.now().timestamp()}",
        name=f"AI: {request.prompt}",
        type="bar",
        config=mock_config,
        workspace_id=request.workspace_id,
        created_by=current_user.id,
        created_at=datetime.now().isoformat(),
        is_ai_generated=True
    )
    
    return chart

@app.get("/api/charts")
async def get_charts(current_user: User = Depends(get_current_user)):
    # Mock charts
    return [
        {
            "id": "1",
            "name": "Sales Performance",
            "type": "bar",
            "workspace_id": current_user.workspace_id,
            "created_by": current_user.id,
            "created_at": "2024-01-15",
            "is_ai_generated": False
        }
    ]

@app.get("/api/dashboards")
async def get_dashboards(current_user: User = Depends(get_current_user)):
    # Mock dashboards
    return [
        {
            "id": "1",
            "name": "Executive Dashboard",
            "description": "High-level business metrics",
            "workspace_id": current_user.workspace_id,
            "charts": ["1", "2", "3"],
            "created_at": "2024-01-15"
        }
    ]

@app.get("/api/analytics/usage")
async def get_usage_analytics(current_user: User = Depends(get_current_user)):
    # Mock analytics data
    return {
        "total_dashboards": 24,
        "active_users": 156,
        "data_sources": 8,
        "charts_created": 89,
        "monthly_trends": [
            {"month": "Jan", "users": 400, "dashboards": 240},
            {"month": "Feb", "users": 300, "dashboards": 139},
            {"month": "Mar", "users": 200, "dashboards": 980},
            {"month": "Apr", "users": 278, "dashboards": 390},
            {"month": "May", "users": 189, "dashboards": 480},
            {"month": "Jun", "users": 239, "dashboards": 380}
        ]
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)