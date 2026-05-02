from celery import Celery
from celery.schedules import crontab
from app import app as flask_app
from config import Config


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=Config.CELERY_RESULT_BACKEND,
        broker=Config.CELERY_BROKER_URL
    )
    
    # Update celery config from app config
    celery.conf.update(
        CELERY_TASK_SERIALIZER='json',
        CELERY_RESULT_SERIALIZER='json',
        CELERY_ACCEPT_CONTENT=['json'],
        CELERY_TIMEZONE='Asia/Kolkata',
        CELERY_ENABLE_UTC=True,
        CELERY_TASK_TRACK_STARTED=True,
        CELERY_TASK_TIME_LIMIT=30 * 60,
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
        'schedule': crontab(hour=9, minute=0),  # 9 AM daily
    },
    'monthly-report': {
        'task': 'tasks.email_tasks.send_monthly_report',
        'schedule': crontab(day_of_month=1, hour=8, minute=0),  # 1st of month at 8 AM
    }
}

celery_app.conf.timezone = 'Asia/Kolkata'
from tasks import email_tasks, export_tasks
