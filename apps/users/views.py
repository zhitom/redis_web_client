# encoding:utf-8
from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import DctUser
from .forms import LoginForms

from public.redis_api import check_connect
from redis_web_client.settings import base
from utils.utils import LoginRequiredMixin
from public.menu import Menu
# Create your views here.


class CustomBackend(ModelBackend):
	def authenticate(self, username=None, password=None, **kwargs):
		try:
			user = DctUser.objects.get(Q(username=username) | Q(email=username))
			if user.check_password(password):
				return user
		except Exception as e:
			return None


class LogoutView(View):
	"""用户登出"""
	def get(self, request):
		logout(request)
		return HttpResponseRedirect(reverse("login"))


class LoginViews(View):
	"""用户登陆"""
	def get(self, request):
		return render(request, 'login.html', {})

	def post(self, request):
		login_form = LoginForms(request.POST)
		nexts = request.get_full_path(force_append_slash=True)
		if login_form.is_valid():
			user_name = request.POST.get("username", "")
			pass_word = request.POST.get("password", "")
			user = authenticate(username=user_name, password=pass_word)
			if user is not None:
				if user.is_active:
					login(request, user)
					servers = base['servers']
					for server in servers:
						status = check_connect(server['host'], server['port'],
				                       password=server.has_key('password') and server['password'] or None)
						if status is not True:
							return HttpResponseRedirect(reverse("redis_error"))
					else:
						return HttpResponseRedirect(reverse("index"))
				else:
					return render(request, "login.html", {"msg": u"用户未激活"})
			else:
				return render(request, "login.html", {"msg": u"用户名或密码错误！"})
		return render(request, "login.html", {'msg': 'error'})


class ChangeUser(LoginRequiredMixin, View):
	def get(self, request):
		menu = Menu()
		id = request.GET.get('id', None)
		try:
			user = DctUser.objects.get(id=id)
		except Exception as e:
			user_error = e

		return render(request, 'change_user.html', {
			'menu': menu,
			'user_info': user,
		})

	def post(self, request):
		menu = Menu()

		id = request.POST.get('id', None)
		username = request.POST.get('username', None)
		password1 = request.POST.get('password1', None)
		password2 = request.POST.get('password2', None)
		email = request.POST.get('email', None)
		permission = int(request.POST.get('permission', None))
		user_error = ''

		try:
			user = DctUser.objects.get(id=id)
			if password1 and password2:
				if password1 == password2:
					user.set_password(password1)
				else:
					user_error = '密码不一致'

			user.email = email
			user.permission = permission
			user.save()

		except Exception as e:
			user_error = e

		return render(request, 'change_user.html', {
			'menu': menu,
			'user_info': user,
			'user_error': user_error
		})


class AddUser(LoginRequiredMixin, View):
	def get(self, request):
		menu = Menu()

		return render(request, 'add_user.html', {
			'menu': menu,
		})

	def post(self, request):
		menu = Menu()

		username = request.POST.get('username', None)
		password1 = request.POST.get('password1', None)
		password2 = request.POST.get('password2', None)
		email = request.POST.get('email', None)
		permission = request.POST.get('permission', None)

		if username and email and permission and password1 == password2:
			try:
				user = DctUser.objects.create_user(username=username,email=email,password=password1)
				user.permission = permission
				user.save()
				return HttpResponseRedirect(reverse("user_manage"))
			except Exception as e:
				return render(request, 'add_user.html', {
					'menu': menu,
					'user_error': e,
				})


