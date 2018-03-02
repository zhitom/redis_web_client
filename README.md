## redis admin
### 安装
#### 环境 python 2.7

```
mkdir -p /data/wwwroot/ && cd /data/wwwroot
git clone https://gitee.com/careyjike_173/redis_web_client.git redis_admin
cd redis_admin && pip install -r requirements.txt
```

### database配置   
默认使用`sqlite3`  
只用于用户登录和删除修改记录等，推荐默认   
修改为`mysql`, `vim redis_admin/settings.py` 修改`DATABASES`部分
安装`pip install MySQL-python==1.2.5`
  
### redis配置  
  `vim conf/conf.py` `base`部分
  
  ```
  # redis 配置
  base = {
    'servers': [
              {
               'index': 0,  // 索引, 新增一个redis加1即可
               'name': 'redis0', // 名称, 为redis命名, 方便菜单栏
               'host': '10.0.20.203', // redis连接地址
               'port': 8000,  // redis端口
               'password': '',  // redis密码
               'databases': 16  // redis配置中可使用多少个db
              # }, {
              #  'index': 1,
              #  'name': 'redis1',
              #  'host': '10.0.20.132',
              #  'port': 6379,
              #  'password': '',
              #  'databases': 16
              }
          ],
    'seperator': ':',
    'maxkeylen': 100
  }
  
  # 项目配置
  DEBUG = False # 关闭debug
  LOG_LEVEL = 'INFO' # 设置日志级别
  ```
  
### nginx
安装nginx, 使用我的另一个开源安装脚本安装nginx

```
git clone https://gitee.com/careyjike_173/script.git
cd script && ./installl
// 根据提示安装nginx
```
配置nginx

```
  server {
  listen 80;
  server_name _;
  access_log /data/wwwlogs/access_nginx.log combined;
  index index.html index.htm index.php;
  location / {
    proxy_pass http://127.0.0.1:8000;
  }
  location /static {
                expires 7d;
                autoindex on;
                add_header Cache-Control provate;
                alias /data/wwwroot/redis_admin/static;
        }
  }
```

### 启动
启动 `redis_admin`

```
chmod +x start.sh
./start.sh start
```
启动`nginx`

```
service nginx start
```

使用`python manage.py createsuperuser` 创建用户  
**访问浏览器 http://ip/** 

![](https://gitee.com/careyjike_173/redis_web_client/raw/master/static/img/1.png)


![](https://gitee.com/careyjike_173/redis_web_client/raw/master/static/img/2.png)

![](https://gitee.com/careyjike_173/redis_web_client/raw/master/static/img/3.png)