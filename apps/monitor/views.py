# coding:utf-8
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import logging
import time

from redis_web_client.settings import base
from redis_web_client import settings
from public.menu import Menu
from public.redis_api import check_connect, get_tmp_client
from utils.utils import LoginRequiredMixin

# Create your views here.
logs = logging.getLogger('django')


class GetRedisInfo(LoginRequiredMixin, View):
	"""
	首页
	获取redis info信息
	"""
	def get(self, request):
		menu = Menu()
		servers = base['servers']
		data = []
		for server in servers:
			status = check_connect(server['host'], server['port'],
			                       password=server.has_key('password') and server['password'] or None)
			if status is True:
				host = {'host': server['host'], 'name': server['name']}
				client = get_tmp_client(host=server['host'], port=server['port'],
				                        password=server.has_key('password') and server['password'] or None)
				info_dict = client.info()
				time_local = time.localtime(info_dict['rdb_last_save_time'])
				dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
				info_dict['rdb_last_save_time'] = dt
				info_dict.update(host)
				data.append(info_dict)

		return render(request, 'index.html', {
			'data': data,
			'menu': menu,
			'console': 'console',
		})


class RedisErrorHtmlView(LoginRequiredMixin, View):
	"""
	错误页视图
	"""
	def get(self, request):
		menu = Menu()
		return render(request, 'redis_error.html', {
			'menu': menu,
			'error': 'error',
		})


class CheckRedisContent(LoginRequiredMixin, View):
	"""
	获取连接错误信息
	"""
	def get(self, request):
		servers = base['servers']
		list = []
		for server in servers:
			status = check_connect(server['host'], server['port'],
			                       password=server.has_key('password') and server['password'] or None)
			if status is not True:
				info_dict = {'name': server['name'], 'host': server['host'], 'port': server['port'], 'error': status.message}
				list.append(info_dict)
		if len(list) != 0:
			data = {'code': 0, 'msg': '', 'data': list}
		else:
			data = {'code': 1, 'msg': '无连接错误', 'data': ''}

		return JsonResponse(data)


class GetKeyView(LoginRequiredMixin, View):
	"""
	获取key
	"""
	def get(self, request, redis_id, db_id):
		from public.redis_api import get_cl, get_all_keys_tree

		values = []
		"搜索"
		search_name = request.GET.get('key[id]', None)
		"分页"
		limit = int(request.GET.get('limit', 30))
		page = int(request.GET.get('page', 1))
		max_num = limit * page
		min_num = max_num - limit

		cl, cur_server_index, cur_db_index = get_cl(int(redis_id), int(db_id))
		if search_name is not None:
			keys = get_all_keys_tree(client=cl, key=search_name, cursor=0, min_num=min_num, max_num=max_num)
		else:
			keys = get_all_keys_tree(client=cl, cursor=0, min_num=min_num, max_num=max_num)
		for key in keys:
			values.append({'key': key})

		db_key_num = cl.dbsize()
		batch_key_num = settings.scan_batch
		if batch_key_num > db_key_num:
			key_num = db_key_num
		else:
			key_num = batch_key_num
		key_value_dict = {'code': 0, 'msg': '', 'count': key_num, 'data': values}

		return JsonResponse(key_value_dict, safe=False)


class GetValueView(LoginRequiredMixin, View):
	"""
	获取key对应value
	"""
	def get(self, request, value_redis_id, value_db_id, key):
		from public.redis_api import get_cl
		from public.data_view import get_value
		cl, cur_server_index, cur_db_index = get_cl(int(value_redis_id), int(value_db_id))
		value_dict = {'code': 0, 'msg': '', 'data': ''}
		if cl.exists(key):
			value = get_value(key, cur_server_index, cur_db_index, cl)
			value_dict['data'] = value
		else:
			value_dict['code'] = 1

		return JsonResponse(value_dict, safe=False)


class GetIdView(LoginRequiredMixin, View):
	def get(self, request, server_id, id):
		menu = Menu()
		server_name = 'redis' + server_id
		return render(request, 'keyvalue.html', {
			'server_id': server_id,
			'db_id': id,
			'menu': menu,
			'server_name': server_name,
			'db_num': 'db'+str(id),
		})


class ClientListView(LoginRequiredMixin, View):
	"""
	获取客户端主机
	"""
	def get(self, request):
		client_id = request.GET.get('client_id', None)
		if client_id is not None:
			server = base['servers'][int(client_id)]
			status = check_connect(host=server['host'], port=server['port'],
			                       password=server.has_key('password') and server['password'] or None)
			if status is True:
				client = get_tmp_client(host=server['host'], port=server['port'],
				                        password=server.has_key('password') and server['password'] or None)
				client_list = client.client_list()
				"分页"
				limit = int(request.GET.get('limit', 30))
				page = int(request.GET.get('page', 1))
				max_num = limit * page
				min_num = max_num - limit

				data = {'code': 0, 'msg': '', 'count': len(client_list), 'data': client_list[min_num:max_num]}
		else:
			data = {'code': 1, 'msg': 'Error, 请联系系统管理员！', 'data': ''}

		return JsonResponse(data, safe=False)


class ClientHtmlView(LoginRequiredMixin, View):
	def get(self, request, client_id):
		menu = Menu()

		return render(request, 'client_list.html', {
			'client_id': client_id,
			'menu': menu
		})


class DelKeyView(LoginRequiredMixin, View):
	"""
	删除key
	"""
	def post(self, request):
		from public.data_change import ChangeData
		from loginfo.models import OperationInfo
		from public.redis_api import get_cl
		from public.data_view import get_value

		server_id = request.POST.get('server_id', None)
		db_id = request.POST.get('db_id', None)
		key = request.POST.get('key', None)

		cl, cur_server_index, cur_db_index = get_cl(int(server_id), int(db_id))
		old_data = get_value(key, cur_server_index, cur_db_index, cl)
		db = OperationInfo(
			username=request.user.username,
			server=server_id,
			db=db_id,
			key=key,
			old_value=old_data,
			type='del',
		)
		db.save()

		if key:
			ch_data = ChangeData(redis_id=server_id, db_id=db_id)

			if ch_data.delete_key(key=key):
				data = {'code': 0, 'msg': 'KEY: ' + key + ' is Success', 'data': ''}
				return JsonResponse(data)

		data = {'code': 1, 'msg': 'KEY: ' + key + ' is Failed', 'data': ''}

		return JsonResponse(data)


class EditValueTableView(LoginRequiredMixin, View):
	def get(self, request, edit_server_id, edit_db_id):
		menu = Menu()
		from public.redis_api import get_cl
		from public.data_view import get_value
		cl, cur_server_index, cur_db_index = get_cl(int(edit_server_id), int(edit_db_id))
		key = request.GET.get('key', None)
		if cl.exists(key):
			value = get_value(key, cur_server_index, cur_db_index, cl)
			if cl.type(key) == 'list':
				value_list = []
				num = 0
				for i in value['value']:
					value_dict = {str(num): i}
					num += 1
					value_list.append(value_dict)
				value['value'] = value_list

		return render(request, 'edit.html', {
			'menu': menu,
			'server_name': 'redis' + edit_server_id,
			'db_num': 'db' + str(edit_db_id),
			'redis_id': edit_server_id,
			'data': value,
		})

	def post(self, request, edit_server_id, edit_db_id):
		from public.data_change import ChangeData
		from public.redis_api import get_cl
		from public.data_view import get_value
		from loginfo.models import OperationInfo

		cl, cur_server_index, cur_db_index = get_cl(int(edit_server_id), int(edit_db_id))
		ch_data = ChangeData(redis_id=edit_server_id, db_id=edit_db_id)
		menu = Menu()

		key = request.GET.get('key', None)
		post_key_type = request.POST.get('Type', None)
		old_data = get_value(key, cur_server_index, cur_db_index, cl)

		if post_key_type == 'string':
			post_value = request.POST.get('value', None)
			ch_data.edit_value(key=key, value=None, new=post_value, score=None)
		elif post_key_type == 'zset':
			score = request.POST.get('Score', None)
			value = request.POST.get('Value', None)
			old_value = request.POST.get('Old_Value', None)
			ch_data.edit_value(key=key, value=old_value, new=value, score=score)
		elif post_key_type == 'set':
			value = request.POST.get('Value', None)
			old_value = request.POST.get('Old_Value', None)
			ch_data.edit_value(key=key, value=old_value, new=value, score=None)
		elif post_key_type == 'hash':
			value_key = request.POST.get('Key', None)
			value = request.POST.get('Value', None)
			ch_data.edit_value(key=key, value=value_key, new=value, score=None)
		elif post_key_type == 'list':
			index = request.POST.get('Index', None)
			value = request.POST.get('Value', None)
			ch_data.edit_value(key=key, value=index, new=value, score=None)

		data = get_value(key, cur_server_index, cur_db_index, cl)
		if cl.type(key) == 'list':
			value_list = []
			num = 0
			for i in data['value']:
				value_dict = {str(num): i}
				num += 1
				value_list.append(value_dict)
			data['value'] = value_list

		db = OperationInfo(
			username=request.user.username,
			server='redis' + edit_server_id,
			db='db' + edit_db_id,
			key=key,
			old_value=old_data,
			value=data,
			type='edit',
		)
		db.save()

		return render(request, 'edit.html', {
			'menu': menu,
			'server_name': 'redis' + edit_server_id,
			'db_num': 'db' + str(edit_db_id),
			'redis_id': edit_server_id,
			'data': data
		})


class BgSaveView(LoginRequiredMixin, View):
	def get(self, request, bg_server_id):
		from public.redis_api import get_cl
		cl, cur_server_index, cur_db_index = get_cl(redis_id=bg_server_id, db_id=0)
		cl.bgsave()

		return HttpResponseRedirect(reverse("index"))


class AddKeyView(LoginRequiredMixin, View):
	def get(self, request, add_redis_id):
		menu = Menu()
		this_tab = 'string'

		return render(request, 'add_key.html', {
			'menu': menu,
			'this_tab': this_tab
		})

	def post(self, request, add_redis_id):
		from public.data_change import ChangeData
		db_id = request.POST.get('db_id', None)
		type = request.POST.get('type', None)
		key = request.POST.get('key', None)
		value = request.POST.get('value', None)

		ch_data = ChangeData(redis_id=add_redis_id, db_id=db_id)
		if type == 'string':
			ch_data.add_key(key=key, value=value, type=type)
		elif type == 'zset':
			score = request.POST.get('score', None)
			ch_data.add_key(key=key, value=value, score=int(score), type=type)
		elif type == 'set':
			ch_data.add_key(key=key, value=value, type=type)
		elif type == 'hash':
			vkey = request.POST.get('vkey', None)
			ch_data.add_key(key=key, vkey=vkey, value=value, type=type)
		elif type == 'list':
			ch_data.add_key(key=key, value=value, type=type)

		return HttpResponseRedirect('/redis'+add_redis_id+'/db'+db_id+'/')

