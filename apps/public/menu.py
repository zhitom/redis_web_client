#!/usr/bin/env python
# coding:utf-8
__author__ = 'carey'
__date__ = '2017/10/12'

from public.redis_api import get_tmp_client, check_redis_connect, get_redis_conf, get_cl
from users.models import RedisConf


def Menu(user):
    """
    菜单导航
    :return:
    """
    servers = get_redis_conf(index=None, user=user)
    data = []
    m_index = 0
    for ser in servers:
        id = "server%s" % m_index
        status = check_redis_connect(index=ser.redis)
        if status is True:
            redis_obj = RedisConf.objects.get(index=ser.redis)
            data_is = {'name': redis_obj.name, 'status': '0', 'db': ''}
            client, cur_server_index, cur_db_index = get_cl(redis_id=ser.redis)
            info_dict = client.info()
            me = []
            for i in range(redis_obj.database):
                if info_dict.has_key("db%s" % i):
                    count = info_dict["db%s" % i]['keys']
                    m_tar = {"pId": id, "count": count, "name": "db%s" % i}
                else:
                    count = 0
                    m_tar = {"pId:": id, "count": count, "name": "db%s" % i}
                me.append(m_tar)
            data_is['db'] = me
            data.append(data_is)
        m_index += 1
    return data
