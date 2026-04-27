from celery import Celery
from celery.schedules import crontab
from app import app as flask_app


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config.get('result_backend', 'redis://localhost:6379/2'),
        broker=app.config.get('broker_url', 'redis://localhost:6379/1')
    )
    celery.conf.update(app.config)

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
        #'schedule': crontab(hour=9, minute=0),
        'schedule': crontab(),
    },
    'monthly-report': {
        'task': 'tasks.email_tasks.send_monthly_report',
        'schedule': crontab(),
        #'schedule': crontab(day_of_month=1, hour=8, minute=0),
    }
}

celery_app.conf.timezone = 'Asia/Kolkata'
from tasks import email_tasks, export_tasks