#!/usr/bin/env python
# coding:utf-8
__author__ = 'carey'
__date__ = '2017/10/12'

from conf.conf import base


def Menu():
    """
    菜单导航
    :return:
    """
    from public.redis_api import get_tmp_client, check_connect
    servers = base['servers']
    data = []
    m_index = 0
    for server in servers:
        id = "server%s" % m_index
        status = check_connect(server['host'], server['port'],
                               password=server.has_key('password') and server['password'] or None)
        if status is True:
            data_is = {'name': server['name'], 'status': '0', 'db': ''}
            client = get_tmp_client(host=server['host'], port=server['port'],
                                    password=server.has_key('password') and server['password'] or None)
            info_dict = client.info()
            me = []
            for i in range(server["databases"]):
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
