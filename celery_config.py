"""
Celery configuration for async TTS processing.
"""

from celery import Celery
from bot.config import get_config

config = get_config()

# Create Celery app
celery_app = Celery(
    'uzbek_tts_bot',
    broker=config.celery_broker_url,
    backend=config.celery_result_backend
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'tasks.process_tts_task': {'queue': 'tts'},
    },
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Worker settings - use solo pool to avoid fork() issues with asyncio
    worker_pool='solo',  # Critical: solo pool for async compatibility
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['tasks'])
