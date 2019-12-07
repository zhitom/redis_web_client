# 修改说明

此项目来自: **[https://gitee.com/careyjike_173/redis_web_client.git](https://gitee.com/careyjike_173/redis_web_client.git)** ,做了如下修改:

- bug修改
  - 集群模式时查看详细客户端的bug:unhashable type错误

- 功能新增
  - 支持在控制台执行命令
  - 支持命令结果按json展示,并增加多种展示方式
  - 支持key使用/、+等特殊字符
  - docker化,下面的是环境变量含义：
    - ADMIN_MAIL: 管理员地址邮件，非必须
    - WEB_USER：web登录界面使用的用户，默认为admin,启动后使用下面的方法设置密码：
      - 在容器中执行：cd /opt/redis_web_client&&python manage.py changepassword ${WEB_USER}
    - NGINX_PORT：暴露给外部访问端口，为访问入口,默认为9000
    - DJANGO_PORT：nginx和django在数据交互端口，默认为8000
    - WEB_DNS_NAME：如果配置了https在反向代理，这里需要配置反向代理暴露给外部访问的域名信息，默认为：sub.your.com:12379
    - MYSQL_DB_NAME：mysql数据库的实例名，默认为rediswebclient
    - MYSQL_DB_HOST：mysql主机名,默认为127.0.0.1
    - MYSQL_DB_PORT：mysql端口，默认为3306
    - MYSQL_DB_USER：mysql用户名，默认为root
    - MYSQL_DB_PASSWD：mysql密码，默认为rediswebclient@123
    - IS_YOUR_CONF：是否使用自己的配置文件，1：自己配置文件通过挂载的方式覆盖到容器内部，默认为0：使用默认配置文件，包括下面在文件：
      - /opt/redis_web_client/conf/conf.py
      - /opt/redis_web_client/redis_admin/settings.py
      - /opt/redis_web_client/funicorn.py
      - /etc/nginx/nginx.conf
      - /etc/nginx/conf.d/redis_web_client.conf
  - docker镜像下载：docker pull zhitom/rediswebclient

- 将redis配置中的host和name长度做了扩充
- 部署到https环境中,增加CSRF_TRUSTED_ORIGINS的对外域名设置信息:

```python
#redis_admin/settings.py
CSRF_TRUSTED_ORIGINS = [
    # may have to include host AND port
    'sub.your.com:8263',
]
```

- 容器里边nginx配置样例，访问地址： **[http://127.0.0.1:9000/](http://127.0.0.1:9000/)** :

```nginx
#/etc/nginx/nginx.conf
user root;
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

```

```nginx
#/etc/nginx/conf.d/redis_web_client.conf
server {
  listen 9000;
  server_name sub.your.com;
  access_log /var/log/access_nginx.log combined;
  add_header Content-Security-Policy upgrade-insecure-requests;
  index index.html index.htm index.php;
  client_max_body_size 1000M;
  location / {
    proxy_pass http://127.0.0.1:8000;
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
                alias /opt/wwwroot/static;
        }
  }
```

# 下面的是原始的Readme

## redis admin

Redis Admin是一个Redis管理平台，主要用于方便查看Key信息。

目前支持`单机Redis`和`Redis Cluster`模式

如果您有好的建议或需求欢迎私信

## 相关文档
**[WIKI](https://gitee.com/careyjike_173/redis_web_client/wikis/Home)**

## 问题反馈
通过 **[Issues](https://gitee.com/careyjike_173/redis_web_client/issues)** 进行反馈

## 截图

![](https://gitee.com/careyjike_173/redis_web_client/raw/master/static/img/1.png)

![](https://gitee.com/careyjike_173/redis_web_client/raw/master/static/img/2.png)

![](https://gitee.com/careyjike_173/redis_web_client/raw/master/static/img/3.png)
