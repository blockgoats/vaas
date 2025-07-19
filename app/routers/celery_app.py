from celery import Celery
import os

# Configure Celery
celery = Celery(
    'bi_platform',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379'),
    include=['tasks.ai_tasks', 'tasks.data_tasks']
)

# Celery configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'tasks.ai_tasks.generate_chart_from_prompt': {'queue': 'ai_queue'},
        'tasks.data_tasks.sync_data_source': {'queue': 'data_queue'},
    }
)

# Periodic tasks
celery.conf.beat_schedule = {
    'sync-data-sources': {
        'task': 'tasks.data_tasks.sync_all_data_sources',
        'schedule': 300.0,  # Every 5 minutes
    },
    'cleanup-old-charts': {
        'task': 'tasks.data_tasks.cleanup_old_charts',
        'schedule': 86400.0,  # Daily
    },
}