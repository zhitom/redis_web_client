# coding=utf-8
import redis
import socket
import sys
import logging

from conf.conf import base, socket_timeout,  scan_batch
from redis.exceptions import (
    RedisError,
    ConnectionError,
    TimeoutError,
    BusyLoadingError,
    ResponseError,
    InvalidResponse,
    AuthenticationError,
    NoScriptError,
    ExecAbortError,
    ReadOnlyError
)
from redis._compat import nativestr

client = None
server_ip = None
db_index = None
logs = logging.getLogger('django')


def connect(*args, **kwargs):
    """ 连接Redis数据库，参数和redis-py的Redis类一样 """
    global client
    client = redis.Redis(*args, **kwargs)


def get_client(*args, **kwargs):
    global server_ip
    global db_index
    if args or kwargs:
        if server_ip!=None and db_index!=None:
            if kwargs['host']==server_ip and kwargs['db']==db_index:
                pass
            else:
                print 'switch conn...'
                connect(*args, **kwargs)
                server_ip = kwargs['host']
                db_index = kwargs['db']
        else:
            print 'init conn...'
            connect(*args, **kwargs)
            server_ip = kwargs['host']
            db_index = kwargs['db']
            
    global client
    if client:
        return client
    else:
        connect(host='127.0.0.1', port=6379)
        return client


def get_tmp_client(*args, **kwargs):
    from redis import Redis
    return Redis(*args, **kwargs)


def get_all_keys_dict(client=None):
    if client:
        m_all = client.keys()
    else:
        m_all = get_client().keys()
    m_all.sort()
    me = {}
    for key in m_all:
        if len(key)>100:
            continue
        key_levels = key.split(base['seperator'])
        cur = me
        for lev in key_levels:
            if cur.has_key(lev):
                if cur.keys()==0:
                    cur[lev] = {lev:{}}#append(lev)
            else:
                cur[lev] = {}
            cur = cur[lev]
    return me


def get_all_keys_tree(client=None,key='*', cursor=0, min_num=None, max_num=None):
    client = client or get_client()
    key = key or '*'
    if key=='*':
        next_cursor,key_all = client.scan(cursor=cursor, match=key, count=scan_batch)
    else:
        key = '*%s*'%key
        next_cursor,key_all = 0, client.keys(key)
    key_all = key_all[min_num:max_num]
    key_all.sort()
    return key_all


def check_connect(host, port, password=None, socket_timeout=socket_timeout):
    # from redis import Connection
    try:
        conn = Connection(host=host, port=port, password=password, socket_timeout=socket_timeout)
        conn.connect()
        return True
    except Exception as e:
        logs.error(e)
        return e


def get_cl(redis_id, db_id):
    cur_server_index = int(redis_id)
    cur_db_index = int(db_id)
    server = base['servers'][cur_server_index]
    cl = get_client(host=server['host'], port=server['port'], db=cur_db_index,
                    password=server.has_key('password') and server['password'] or None)
    return cl, cur_server_index, cur_db_index


class Connection(redis.Connection):
    """
    继承redis Connection
    """
    def connect(self):
        "Connects to the Redis server if not already connected"
        if self._sock:
            return
        try:
            sock = self._connect()
        except socket.error:
            e = sys.exc_info()[1]
            raise ConnectionError(self._error_message(e))

        self._sock = sock
        try:
            self.on_connect()
        except RedisError:
            # clean up after any error in on_connect
            self.disconnect()
            raise

        # run any user callbacks. right now the only internal callback
        # is for pubsub channel/pattern resubscription
        for callback in self._connect_callbacks:
            callback(self)

    def on_connect(self):
        "Initialize the connection, authenticate and select a database"
        self._parser.on_connect(self)

        # if a password is specified, authenticate
        if self.password:
            self.send_command('AUTH', self.password)
            if nativestr(self.read_response()) != 'OK':
                raise AuthenticationError('Invalid Password')

        # if a database is specified, switch to it
        if self.db >= 0: # 密码为空，切换db判断是否需要认证
            self.send_command('SELECT', self.db)
            if nativestr(self.read_response()) != 'OK':
                raise ConnectionError('Invalid Database')