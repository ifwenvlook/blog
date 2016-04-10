#!/bin/bash

service mysqld stop
service nginx stop
killall -9 uwsgi
