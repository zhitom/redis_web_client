#!/bin/sh

imagename="rediswebclient"
hosturl="zhitom" #hub.docker.com的帐号名

yourimgtag="${imagename}"
yourimg=`echo ${yourimgtag}|awk -F: '{print $1}'`
yourtag=`echo ${yourimgtag}|awk -F: '{print $2}'`
if [ "x$yourtag" = "x" ];then
    yourtag="latest"
fi
harborurl="${hosturl}"
if [ "x$harborurl" = "x" ];then
    harborurl=""
fi
docker rmi ${yourimg}:latest
docker rmi $harborurl/${yourimg}:latest

docker build --no-cache --tag ${yourimg}:latest .

docker tag ${yourimg}:latest $harborurl/${yourimg}:${yourtag}

docker push $harborurl/${yourimg}:${yourtag}

docker rmi $harborurl/${yourimg}:${yourtag}
docker rmi ${yourimg}:latest

