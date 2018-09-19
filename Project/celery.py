from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')

CELERY_BEAT_SCHEDULE = {
    'orders-request-single-minute': {
        'task': 'san_site.tasks.orders_request',
        'schedule': crontab(minute=1)
    }
}

app = Celery('san_site')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0, orders_request.s('test'), name='orders_request')


@app.task
def orders_request(arg):
    from san_site.models import Order
    Order.orders_request()