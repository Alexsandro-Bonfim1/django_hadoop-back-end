from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hadoop_project.settings')

app = Celery('hadoop_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Schedule periodic tasks
app.conf.beat_schedule = {
    'collect-metrics-every-60-seconds': {
        'task': 'hadoop_app.tasks.collect_metrics',
        'schedule': 60.0,
    },
    'check-cluster-health-every-300-seconds': {
        'task': 'hadoop_app.tasks.check_cluster_health',
        'schedule': 300.0,
    },
}
