import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_api.settings')

app = Celery('shop_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'create-minute-heartbeat-log': {
        'task': 'users.tasks.create_crontab_heartbeat_log',
        'schedule': crontab(minute='*/1'),
    },
}
