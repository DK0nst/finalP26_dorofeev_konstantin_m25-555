from celery import Celery
from app.core.config import settings
import app.tasks.llm_tasks

celery_app = Celery(
    "bot_service",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
)

# Дополнительные настройки
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_acks_late=True,           # подтверждение после выполнения
    worker_prefetch_multiplier=1,  # брать по одной задаче
)

# Автоматический поиск задач в пакете app.tasks
celery_app.autodiscover_tasks(["app.tasks"])