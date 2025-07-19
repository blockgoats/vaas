from celery_app import celery
import os
from typing import Dict, Any
import json
from ai.llm_providers import create_llm_manager
from ai.chart_intelligence import ChartIntelligence
from ai.chart_validator import ChartValidator
from ai.iterative_refinement import IterativeChartRefinement
from ai.batch_generation import BatchChartGenerator

# Initialize AI components
llm_manager = create_llm_manager()
chart_intelligence = ChartIntelligence()
chart_validator = ChartValidator()
iterative_refinement = IterativeChartRefinement(llm_manager)
batch_generator = BatchChartGenerator(llm_manager)


@celery.task(bind=True)
def generate_chart_from_prompt(self, prompt: str, data_source_id: str, workspace_id: str, 
                              schema_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Enhanced chart generation with multi-LLM support and intelligence
    """
    
    try:
        # Update task progress
        self.update_state(state='PROGRESS', meta={'current': 10, 'total': 100, 'status': 'Analyzing prompt'})
        
        # Get schema context if not provided
        if not schema_context:
            schema_context = {"tables": []}  # Would fetch from database in production
        
        # Analyze data context
        self.update_state(state='PROGRESS', meta={'current': 20, 'total': 100, 'status': 'Analyzing data context'})
        columns_info = chart_intelligence.analyze_data_context(schema_context)
        
        # Get chart recommendations
        self.update_state(state='PROGRESS', meta={'current': 30, 'total': 100, 'status': 'Getting chart recommendations'})
        recommendations = chart_intelligence.recommend_charts(prompt, columns_info)
        
        # Generate chart using LLM
        self.update_state(state='PROGRESS', meta={'current': 50, 'total': 100, 'status': 'Generating chart with AI'})
        llm_response = await llm_manager.generate_chart(prompt, schema_context)
        
        # Validate generated chart
        self.update_state(state='PROGRESS', meta={'current': 70, 'total': 100, 'status': 'Validating chart'})
        validation_result = chart_validator.validate_chart(
            llm_response.chart_config, prompt, schema_context
        )
        
        # Apply auto-fixes if needed
        if validation_result.auto_fixes:
            for field, fix_value in validation_result.auto_fixes.items():
                llm_response.chart_config[field] = fix_value
        
        # Update task progress
        self.update_state(state='PROGRESS', meta={'current': 90, 'total': 100, 'status': 'Finalizing'})
        
        # Prepare response
        response = {
            'status': 'SUCCESS',
            'result': {
                'chart_type': llm_response.chart_type,
                'title': llm_response.title,
                'sql_query': llm_response.sql_query,
                'chart_config': llm_response.chart_config,
                'confidence': llm_response.confidence,
                'reasoning': llm_response.reasoning
            },
            'recommendations': [
                {
                    'chart_type': rec.chart_type.value,
                    'confidence': rec.confidence,
                    'reasoning': rec.reasoning
                } for rec in recommendations[:3]
            ],
            'validation': {
                'is_valid': validation_result.is_valid,
                'score': validation_result.score,
                'issues': [
                    {
                        'level': issue.level.value,
                        'message': issue.message,
                        'suggestion': issue.suggestion
                    } for issue in validation_result.issues
                ],
                'suggestions': validation_result.suggestions
            },
            'chart_id': f'ai_chart_{workspace_id}_{int(time.time())}'
        }
        
        self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Complete'})
        return response
        
    except Exception as exc:
        self.update_state(
            state='FAILURE',
            meta={'error': str(exc), 'status': 'Failed'}
        )
        raise exc

@celery.task(bind=True)
def suggest_chart_types(self, data_description: str) -> Dict[str, Any]:
    """Get chart type suggestions based on data description"""
    try:
        suggestions = await llm_manager.suggest_chart_type(data_description)
        return {
            'status': 'SUCCESS',
            'suggestions': [
                {
                    'chart_type': s.chart_type,
                    'confidence': s.confidence,
                    'reasoning': s.reasoning,
                    'config': s.config
                } for s in suggestions
            ]
        }
    except Exception as exc:
        return {'status': 'ERROR', 'error': str(exc)}

@celery.task(bind=True)
def validate_chart_config(self, chart_config: Dict[str, Any], original_prompt: str, 
                         schema_context: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a chart configuration"""
    try:
        validation_result = chart_validator.validate_chart(chart_config, original_prompt, schema_context)
        return {
            'status': 'SUCCESS',
            'validation': {
                'is_valid': validation_result.is_valid,
                'score': validation_result.score,
                'issues': [
                    {
                        'level': issue.level.value,
                        'message': issue.message,
                        'suggestion': issue.suggestion,
                        'field': issue.field
                    } for issue in validation_result.issues
                ],
                'suggestions': validation_result.suggestions,
                'auto_fixes': validation_result.auto_fixes
            }
        }
    except Exception as exc:
        return {'status': 'ERROR', 'error': str(exc)}

@celery.task(bind=True)
def process_batch_chart_generation(self, job_id: str, schema_context: Dict[str, Any]) -> Dict[str, Any]:
    """Process a batch chart generation job"""
    try:
        self.update_state(state='PROGRESS', meta={'current': 0, 'total': 100, 'status': 'Starting batch job'})
        
        job = await batch_generator.process_batch_job(job_id, schema_context)
        
        return {
            'status': 'SUCCESS',
            'job': {
                'job_id': job.job_id,
                'status': job.status.value,
                'progress': job.progress,
                'total_requests': job.total_requests,
                'completed_requests': job.completed_requests,
                'failed_requests': job.failed_requests,
                'results': [
                    {
                        'request_id': r.request_id,
                        'chart_config': r.chart_config,
                        'error': r.error,
                        'confidence': r.confidence
                    } for r in job.results
                ]
            }
        }
    except Exception as exc:
        return {'status': 'ERROR', 'error': str(exc)}

@celery.task(bind=True)
def refine_chart_iteratively(self, session_id: str, user_message: str) -> Dict[str, Any]:
    """Process iterative chart refinement"""
    try:
        refinement_response = await iterative_refinement.process_refinement(session_id, user_message)
        
        return {
            'status': 'SUCCESS',
            'refinement': {
                'updated_chart': refinement_response.updated_chart,
                'explanation': refinement_response.explanation,
                'actions_taken': [action.value for action in refinement_response.actions_taken],
                'confidence': refinement_response.confidence,
                'suggestions': refinement_response.suggestions
            }
        }
    except Exception as exc:
        return {'status': 'ERROR', 'error': str(exc)}

@celery.task
def validate_chart_with_zk_proof(chart_config: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
    """
    Optional: Zero-Knowledge proof validation for chart generation.
    Ensures the AI-generated chart actually represents the user's intent.
    
    This is an advanced feature for high-security environments.
    """
    
    # Mock ZK proof validation
    # In reality, this would use cryptographic proofs to verify:
    # 1. The chart was generated from the specified prompt
    # 2. No unauthorized data access occurred
    # 3. The transformation is mathematically sound
    
    return {
        'is_valid': True,
        'proof_hash': 'zk_proof_hash_placeholder',
        'verification_timestamp': '2024-01-24T10:00:00Z'
    }