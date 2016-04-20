#!/bin/bash

service mysqld restart
service nginx  restart
killall -9 uwsgi
uwsgi /home/blog/config.ini 
