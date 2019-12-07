#!/bin/sh
#set -eu
set -x
rootdir="/opt/redis_web_client"

adminmail="shandyshandy@163.com"
if [ "x${ADMIN_MAIL}" != "x" ]; then
    adminmail="${ADMIN_MAIL}"
fi
export ADMIN_MAIL=${adminmail}

webuser="admin"
if [ "x${WEB_USER}" != "x" ]; then
    webuser="${WEB_USER}"
fi
export WEB_USER=${webuser}

#webpasswd="admin@redis"

nginxport="9000"
if [ "x${NGINX_PORT}" != "x" ]; then
    nginxport="${NGINX_PORT}"
fi
export NGINX_PORT=${nginxport}

djangoport="8000"
if [ "x${DJANGO_PORT}" != "x" ]; then
    djangoport="${DJANGO_PORT}"
fi
export DJANGO_PORT=${djangoport}

webdnsname="sub.your.com:12379"
if [ "x${WEB_DNS_NAME}" != "x" ]; then
    webdnsname="${WEB_DNS_NAME}"
fi
export WEB_DNS_NAME=${webdnsname}

mysqlname="rediswebclient"
if [ "x${MYSQL_DB_NAME}" != "x" ]; then
    mysqlname="${MYSQL_DB_NAME}"
fi
export MYSQL_DB_NAME=${mysqlname}

mysqldb="127.0.0.1"
if [ "x${MYSQL_DB_HOST}" != "x" ]; then
    mysqldb="${MYSQL_DB_HOST}"
fi
export MYSQL_DB_HOST=${mysqldb}

mysqlport="3306"
if [ "x${MYSQL_DB_PORT}" != "x" ]; then
    mysqlport="${MYSQL_DB_PORT}"
fi
export MYSQL_DB_PORT=${mysqlport}

mysqluser="rediswebclient"
if [ "x${MYSQL_DB_USER}" != "x" ]; then
    mysqluser="${MYSQL_DB_USER}"
fi
export MYSQL_DB_USER=${mysqluser}

mysqlpasswd="rediswebclient@123"
if [ "x${MYSQL_DB_PASSWD}" != "x" ]; then
    mysqlpasswd="${MYSQL_DB_PASSWD}"
fi
export MYSQL_DB_PASSWD=${mysqlpasswd}

isyourconf=0
if [ "x${IS_YOUR_CONF}" != "x" ]; then
    isyourconf="${IS_YOUR_CONF}"
fi
export IS_YOUR_CONF=${isyourconf}

########################################################
if [ "x${isyourconf}" = "x0" ]; then

#数据库连接信息修改
sed -i "s/redis_admin/${mysqlname}/g;s/127.0.0.1/${mysqldb}/g;s/3306/${mysqlport}/g;s/root/${mysqluser}/g;s/password/password\": \"${mysqlpasswd}\", #/g;" ${rootdir}/conf/conf.py
#修改域名
sed -i "s/sub.your.com:8263/${webdnsname}/g" ${rootdir}/redis_admin/settings.py
sed -i "s/8000/${djangoport}/g" ${rootdir}/funicorn.py

#nginx配置修改
mkdir -p /etc/nginx/conf.d
cat >/etc/nginx/nginx.conf<<EOF
user root; #www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
        worker_connections 768;
        # multi_accept on;
}

http {

        ##
        # Basic Settings
        ##

        #sendfile on;
        #tcp_nopush on;
        #tcp_nodelay on;
        keepalive_timeout 65;
        #types_hash_max_size 2048;
        # server_tokens off;

        # server_names_hash_bucket_size 64;
        # server_name_in_redirect off;

        include /etc/nginx/mime.types;
        default_type application/octet-stream;

        ##
        # SSL Settings
        ##

        #ssl_protocols TLSv1 TLSv1.1 TLSv1.2; # Dropping SSLv3, ref: POODLE
        #ssl_prefer_server_ciphers on;

        ##
        # Logging Settings
        ##
        log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';
        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;

        ##
        # Gzip Settings
        ##

        #gzip on;

        # gzip_vary on;
        # gzip_proxied any;
        # gzip_comp_level 6;
        # gzip_buffers 16 8k;
        # gzip_http_version 1.1;
        # gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
        # map $http_upgrade $connection_upgrade {
        #   default upgrade;
        #   '' close;
        # }
        ##
        # Virtual Host Configs
        ##

        include /etc/nginx/conf.d/*.conf;
        include /etc/nginx/sites-enabled/*;
        
}


#mail {
#       # See sample authentication script at:
#       # http://wiki.nginx.org/ImapAuthenticateWithApachePhpScript
# 
#       # auth_http localhost/auth.php;
#       # pop3_capabilities "TOP" "USER";
#       # imap_capabilities "IMAP4rev1" "UIDPLUS";
# 
#       server {
#               listen     localhost:110;
#               protocol   pop3;
#               proxy      on;
#       }
# 
#       server {
#               listen     localhost:143;
#               protocol   imap;
#               proxy      on;
#       }
#}
EOF
cat >/etc/nginx/conf.d/redis_web_client.conf<<EOF
server {
  listen ${nginxport};
  server_name me.rediswebclient.plat.aivanlink.com;
  access_log ${rootdir}/log/access_nginx.log combined;
  add_header Content-Security-Policy upgrade-insecure-requests;
  index index.html index.htm index.php;
  client_max_body_size 1000M;
  location / {
    proxy_pass http://127.0.0.1:${djangoport};
    # proxy_redirect http:// $scheme://;
    # port_in_redirect on;
    # #proxy_redirect     off;
    # proxy_set_header   Host             $http_host;
    # proxy_set_header   X-Real-IP        $remote_addr:$remote_port;
    # proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
    # proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
    # proxy_set_header X-Forwarded-Proto "https"; 
  }
  location /static {
                expires 7d;
                autoindex on;
                add_header Cache-Control provate;
                alias ${rootdir}/static;
        }
  }
EOF

fi

#启动Django和nginx
echo '================================================================='
echo 'USE THIS FIRSTLY TO CHANGE PASSWORD AT THIS CONTAINER-CONSOLE: python manage.py changepassword ${webuser}'
echo "Default user=${webuser}"
echo '================================================================='
echo 'NOW it is first start...'
cd ${rootdir}&&(python manage.py migrate||exit 0)&&(python manage.py createsuperuser --username ${webuser} --noinput  --email ${adminmail}||exit 0)&& \
        chmod +x start.sh && ./start.sh start 
nginx

#查看日志
tail -f ${rootdir}/log/*
#tail -f /etc/passwd


