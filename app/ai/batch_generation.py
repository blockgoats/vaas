from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
from datetime import datetime
import uuid

class BatchStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ChartRequest:
    id: str
    prompt: str
    data_source_id: Optional[str]
    chart_type_hint: Optional[str]
    priority: int = 1

@dataclass
class ChartResult:
    request_id: str
    chart_config: Optional[Dict[str, Any]]
    error: Optional[str]
    processing_time: float
    confidence: float

@dataclass
class BatchJob:
    job_id: str
    workspace_id: str
    user_id: str
    requests: List[ChartRequest]
    results: List[ChartResult]
    status: BatchStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    progress: float
    total_requests: int
    completed_requests: int
    failed_requests: int

class BatchChartGenerator:
    """Handles batch generation of multiple charts from prompts"""
    
    def __init__(self, llm_manager, max_concurrent_jobs: int = 5):
        self.llm_manager = llm_manager
        self.max_concurrent_jobs = max_concurrent_jobs
        self.active_jobs: Dict[str, BatchJob] = {}
        self.job_queue: List[str] = []
        self.processing_semaphore = asyncio.Semaphore(max_concurrent_jobs)
    
    def create_batch_job(self, workspace_id: str, user_id: str, 
                        chart_requests: List[Dict[str, Any]]) -> str:
        """Create a new batch job for chart generation"""
        
        job_id = str(uuid.uuid4())
        
        # Convert request dicts to ChartRequest objects
        requests = []
        for i, req in enumerate(chart_requests):
            request = ChartRequest(
                id=f"{job_id}_{i}",
                prompt=req["prompt"],
                data_source_id=req.get("data_source_id"),
                chart_type_hint=req.get("chart_type_hint"),
                priority=req.get("priority", 1)
            )
            requests.append(request)
        
        # Sort by priority (higher priority first)
        requests.sort(key=lambda x: x.priority, reverse=True)
        
        job = BatchJob(
            job_id=job_id,
            workspace_id=workspace_id,
            user_id=user_id,
            requests=requests,
            results=[],
            status=BatchStatus.PENDING,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            progress=0.0,
            total_requests=len(requests),
            completed_requests=0,
            failed_requests=0
        )
        
        self.active_jobs[job_id] = job
        self.job_queue.append(job_id)
        
        return job_id
    
    async def process_batch_job(self, job_id: str, schema_context: Dict[str, Any]) -> BatchJob:
        """Process a batch job asynchronously"""
        
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.active_jobs[job_id]
        
        async with self.processing_semaphore:
            job.status = BatchStatus.PROCESSING
            job.started_at = datetime.now()
            
            try:
                # Process requests concurrently with limited concurrency
                semaphore = asyncio.Semaphore(3)  # Max 3 concurrent chart generations
                
                async def process_single_request(request: ChartRequest) -> ChartResult:
                    async with semaphore:
                        return await self._process_chart_request(request, schema_context)
                
                # Create tasks for all requests
                tasks = [process_single_request(req) for req in job.requests]
                
                # Process with progress tracking
                results = []
                for i, task in enumerate(asyncio.as_completed(tasks)):
                    result = await task
                    results.append(result)
                    
                    # Update progress
                    job.completed_requests = i + 1
                    if result.error:
                        job.failed_requests += 1
                    
                    job.progress = (job.completed_requests / job.total_requests) * 100
                
                job.results = results
                job.status = BatchStatus.COMPLETED
                job.completed_at = datetime.now()
                
            except Exception as e:
                job.status = BatchStatus.FAILED
                job.completed_at = datetime.now()
                # Add error result for debugging
                job.results.append(ChartResult(
                    request_id="batch_error",
                    chart_config=None,
                    error=str(e),
                    processing_time=0.0,
                    confidence=0.0
                ))
        
        return job
    
    async def _process_chart_request(self, request: ChartRequest, 
                                   schema_context: Dict[str, Any]) -> ChartResult:
        """Process a single chart request"""
        
        start_time = datetime.now()
        
        try:
            # Generate chart using LLM
            llm_response = await self.llm_manager.generate_chart(
                request.prompt, schema_context
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ChartResult(
                request_id=request.id,
                chart_config=llm_response.chart_config,
                error=None,
                processing_time=processing_time,
                confidence=llm_response.confidence
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ChartResult(
                request_id=request.id,
                chart_config=None,
                error=str(e),
                processing_time=processing_time,
                confidence=0.0
            )
    
    def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """Get the current status of a batch job"""
        return self.active_jobs.get(job_id)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or processing job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            if job.status in [BatchStatus.PENDING, BatchStatus.PROCESSING]:
                job.status = BatchStatus.CANCELLED
                job.completed_at = datetime.now()
                return True
        return False
    
    def get_job_results(self, job_id: str) -> Optional[List[ChartResult]]:
        """Get results from a completed job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            if job.status == BatchStatus.COMPLETED:
                return job.results
        return None
    
    def cleanup_completed_jobs(self, max_age_hours: int = 24):
        """Clean up old completed jobs"""
        current_time = datetime.now()
        jobs_to_remove = []
        
        for job_id, job in self.active_jobs.items():
            if job.completed_at:
                age_hours = (current_time - job.completed_at).total_seconds() / 3600
                if age_hours > max_age_hours:
                    jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.active_jobs[job_id]
            if job_id in self.job_queue:
                self.job_queue.remove(job_id)
    
    def get_user_jobs(self, user_id: str) -> List[BatchJob]:
        """Get all jobs for a specific user"""
        return [job for job in self.active_jobs.values() if job.user_id == user_id]
    
    def get_workspace_jobs(self, workspace_id: str) -> List[BatchJob]:
        """Get all jobs for a specific workspace"""
        return [job for job in self.active_jobs.values() if job.workspace_id == workspace_id]
    
    async def create_dashboard_from_batch(self, job_id: str, dashboard_name: str) -> Dict[str, Any]:
        """Create a dashboard from successful batch results"""
        
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.active_jobs[job_id]
        
        if job.status != BatchStatus.COMPLETED:
            raise ValueError(f"Job {job_id} is not completed")
        
        # Get successful results
        successful_results = [r for r in job.results if r.chart_config and not r.error]
        
        if not successful_results:
            raise ValueError("No successful charts to create dashboard")
        
        # Create dashboard configuration
        dashboard_config = {
            "id": str(uuid.uuid4()),
            "name": dashboard_name,
            "description": f"Auto-generated dashboard from batch job {job_id}",
            "workspace_id": job.workspace_id,
            "created_by": job.user_id,
            "created_at": datetime.now().isoformat(),
            "charts": [
                {
                    "id": result.request_id,
                    "config": result.chart_config,
                    "position": self._calculate_chart_position(i, len(successful_results))
                }
                for i, result in enumerate(successful_results)
            ],
            "layout": self._generate_dashboard_layout(len(successful_results))
        }
        
        return dashboard_config
    
    def _calculate_chart_position(self, index: int, total_charts: int) -> Dict[str, int]:
        """Calculate optimal position for chart in dashboard grid"""
        
        # Simple grid layout calculation
        cols = min(3, total_charts)  # Max 3 columns
        rows = (total_charts + cols - 1) // cols  # Calculate needed rows
        
        row = index // cols
        col = index % cols
        
        return {
            "x": col * 4,  # Each chart takes 4 grid units width
            "y": row * 3,  # Each chart takes 3 grid units height
            "w": 4,        # Width in grid units
            "h": 3         # Height in grid units
        }
    
    def _generate_dashboard_layout(self, chart_count: int) -> Dict[str, Any]:
        """Generate optimal dashboard layout"""
        
        return {
            "grid_size": 12,  # 12-column grid
            "row_height": 100,  # Height of each row in pixels
            "margin": [10, 10],  # Margin between charts
            "responsive": True,
            "auto_size": True
        }

# Example usage patterns
class BatchTemplates:
    """Pre-defined batch generation templates"""
    
    @staticmethod
    def executive_dashboard() -> List[Dict[str, Any]]:
        """Generate executive dashboard charts"""
        return [
            {
                "prompt": "Show monthly revenue trends for the last 12 months",
                "priority": 5,
                "chart_type_hint": "line"
            },
            {
                "prompt": "Display top 10 products by sales volume",
                "priority": 4,
                "chart_type_hint": "bar"
            },
            {
                "prompt": "Show customer acquisition by channel",
                "priority": 3,
                "chart_type_hint": "pie"
            },
            {
                "prompt": "Display regional sales performance",
                "priority": 3,
                "chart_type_hint": "bar"
            },
            {
                "prompt": "Show profit margin trends over time",
                "priority": 2,
                "chart_type_hint": "line"
            }
        ]
    
    @staticmethod
    def marketing_dashboard() -> List[Dict[str, Any]]:
        """Generate marketing dashboard charts"""
        return [
            {
                "prompt": "Show website traffic by source for last 6 months",
                "priority": 5,
                "chart_type_hint": "area"
            },
            {
                "prompt": "Display conversion rates by campaign",
                "priority": 4,
                "chart_type_hint": "bar"
            },
            {
                "prompt": "Show email campaign performance metrics",
                "priority": 3,
                "chart_type_hint": "line"
            },
            {
                "prompt": "Display social media engagement trends",
                "priority": 3,
                "chart_type_hint": "line"
            },
            {
                "prompt": "Show lead generation by channel",
                "priority": 2,
                "chart_type_hint": "pie"
            }
        ]
    
    @staticmethod
    def operations_dashboard() -> List[Dict[str, Any]]:
        """Generate operations dashboard charts"""
        return [
            {
                "prompt": "Show production efficiency trends",
                "priority": 5,
                "chart_type_hint": "line"
            },
            {
                "prompt": "Display inventory levels by category",
                "priority": 4,
                "chart_type_hint": "bar"
            },
            {
                "prompt": "Show quality metrics over time",
                "priority": 3,
                "chart_type_hint": "line"
            },
            {
                "prompt": "Display supplier performance ratings",
                "priority": 3,
                "chart_type_hint": "heatmap"
            },
            {
                "prompt": "Show cost breakdown by department",
                "priority": 2,
                "chart_type_hint": "pie"
            }
        ]

# Global instance
batch_generator = BatchChartGenerator(None)  # Will be initialized with LLM manager