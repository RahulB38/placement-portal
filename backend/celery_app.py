import os
from celery import Celery
from celery.schedules import crontab
from app import app as flask_app

def make_celery(app):
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

    celery = Celery(
        app.import_name,
        backend=redis_url,
        broker=redis_url
    )

    # new-style settings only
    celery.conf.update(
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='Asia/Kolkata',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery_app = make_celery(flask_app)

celery_app.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'tasks.email_tasks.send_daily_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
    'monthly-report': {
        'task': 'tasks.email_tasks.send_monthly_report',
        'schedule': crontab(day_of_month=1, hour=8, minute=0),
    }
}

celery_app.conf.timezone = 'Asia/Kolkata'

from tasks import email_tasks, export_tasks
