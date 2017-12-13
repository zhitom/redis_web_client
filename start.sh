#!/bin/bash

start() {
    gunicorn -c funicorn.py redis_web_client.wsgi
    if [ $? -eq 0 ]; then
        echo 'start [ ok ]'
    else
        echo 'start [ no ]'
    fi
}

stop() {
    pid=`cat /data/wwwroot/redis_web_client/log/gunicorn.pid`
    kill ${pid}
    if [ $? -eq 0 ]; then
        echo 'stop [ ok ]'
    else
        echo 'stop [ no ]'
    fi
}

$1