#!/bin/bash

start() {
    source activate py27
    gunicorn -c funicorn.py dct_redis.wsgi
    if [ $? -eq 0 ]; then
        echo 'start [ ok ]'
    else
        echo 'start [ no ]'
    fi
}

stop() {
    pid=`cat /data/wwwlogs/gunicorn.pid`
    kill ${pid}
    if [ $? -eq 0 ]; then
        echo 'stop [ ok ]'
    else
        echo 'stop [ no ]'
    fi
}

$1