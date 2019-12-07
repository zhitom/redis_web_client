##################################################################################
#jdk-1.8.0_222 maven-3.6.2 gradle-5.6.2 docker-18.09.8 git-2.11.0 nodejs-0.12
#docker run --rm -it java-compile-docker:latest bash
##################################################################################
FROM debian:buster-slim
LABEL maintainer="shandyshandy@163.com"
##################################################################################
#modify timezone
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
##################################################################################
#modify sources.list
RUN mv /etc/apt/sources.list /etc/apt/sources.list.orig
COPY sources.list /etc/apt/
##################################################################################
#modify shell
RUN (rm -rf /bin/sh || exit 0) && ln -s /bin/bash /bin/sh
##################################################################################
#install softs
RUN apt-get update || exit 0
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python python-dev python-mysqldb \
    build-essential libmariadb-dev-compat libmariadb-dev \
    vim-tiny procps net-tools lsof inetutils-ping \
    git nginx redis
##################################################################################
#pip conf
RUN mkdir -p /root/.pip
COPY pip.conf /root/.pip/
COPY get-pip.py /root
##################################################################################
#curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN cd /root\
    && python get-pip.py \
    && (rm -rf get-pip.py .cache || exit 0)
#    && python get-pip.py \
#    && pip install distribute \
#    && pip install supervisor \
#    && (rm -rf get-pip.py .cache || exit 0)

##################################################################################
#modify sources.list
COPY docker-entrypoint.sh /root/
RUN chmod 777 /root/docker-entrypoint.sh
ENV USER root
##################################################################################
#install app
RUN mkdir -p /opt&&cd /opt&&git clone https://github.com/zhitom/redis_web_client.git \
    && cd redis_web_client&&(rm -rf .git || exit 0)&& \
    (sed -i 's/free_me/free_me;my_bool reconnect/g' /usr/include/mysql/mysql.h||exit 0)&& \
    pip install -r requirements.txt
##################################################################################
# end
RUN DEBIAN_FRONTEND=noninteractive apt-get purge -q -y python-dev build-essential libmariadb-dev-compat libmariadb-dev
RUN DEBIAN_FRONTEND=noninteractive apt-get autoremove -q -v && apt-get clean && apt-get autoclean
RUN rm -rf /root/.cache || exit 0
ENTRYPOINT ["/root/docker-entrypoint.sh"]
# 为了方便测试
#CMD ["sh","--","tail -f /etc/group"]
#CMD ["sh"]

