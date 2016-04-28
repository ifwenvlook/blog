import os
from app import celery, create_app

app = create_app('default')
app.app_context().push()
#start celery worker -A celery_worker.celery -l INFO  /celery worker -A celery_worker.celery --loglevel=info