from app import create_app, celery

app = create_app()
app.app_context().push()
#start celery worker -A celery_worker.celery -l INFO  /celery worker -A celery_worker.celery --loglevel=info