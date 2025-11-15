import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ku_net.settings")

app = Celery("ku_net")
app.conf.broker_url = "redis://localhost:6379/0"  # make sure Redis is running on this
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
