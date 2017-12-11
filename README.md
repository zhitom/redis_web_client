## redis web client
### 安装

```
python 2.7

pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```

### 相关配置
- database   
  默认使用`sqlite3`  
  只用于用户登录和删除修改记录等，推荐默认   
  修改为`mysql`, `vim redis_web_client/settings.py` 修改`DATABASES`部分
  
- redis  
  `vim redis_web_client/settgins.py` `base`部分
  
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
  ```

访问浏览器http://127.0.0.1:8000/  
访问用户:admin 密码:admin   
可以使用`python manage.py createsuperuser` 创建用户

![](https://gitee.com/careyjike_173/redis_web_client/raw/master/static/img/1.png)


![](https://gitee.com/careyjike_173/redis_web_client/raw/master/static/img/2.png)