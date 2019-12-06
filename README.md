# 说明

此项目来自: **[https://gitee.com/careyjike_173/redis_web_client.git](https://gitee.com/careyjike_173/redis_web_client.git)** ,做了如下修改:

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

- bug修改
  - 集群模式时查看详细客户端的bug:unhashable type错误
- 功能新增
  - 支持在控制台执行命令
  - 支持命令结果按json展示

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
