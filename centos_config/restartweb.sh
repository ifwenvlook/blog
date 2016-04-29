#!/bin/bash

service mysqld restart
service nginx  restart
service redis restart
killall -9 uwsgi
uwsgi /home/blog/config.ini -d /home/log/uwsgi.log
killall -9 celery
cd /home/blog
celery worker -A celery_worker.celery -l INFO &
