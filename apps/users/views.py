# encoding:utf-8
from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse
from .models import DctUser
from .forms import LoginForms

from public.redis_api import check_redis_connect, get_redis_conf
from utils.utils import LoginRequiredMixin
from public.menu import Menu
from users.models import Auth, RedisConf
from public.sendmail import send_email
from conf.conf import mail_receivers
from conf import logs

# Create your views here.


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = DctUser.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            logs.error(e)
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
        data = dict(
            code=0,
            msg=u"登录成功，即将跳转...",
            data="",
        )
        login_form = LoginForms(request.POST)
        nexts = request.get_full_path(force_append_slash=True)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    servers = get_redis_conf(name=None, user=request.user)
                    user_premission = dict()
                    for ser in servers:
                        redis_name = RedisConf.objects.get(id=ser.redis)
                        user_premission[redis_name.name] = ser.pre_auth
                    data["data"] = user_premission
                    return JsonResponse(data)
                else:
                    data["code"] = 1
                    data["msg"] = u"用户未激活"
                    return JsonResponse(data)
        data["code"] = 2
        data["msg"] = u"用户名或密码错误"
        return JsonResponse(data)


class ChangeUser(LoginRequiredMixin, View):
    def get(self, request):
        menu = Menu(user=request.user)
        id = request.GET.get('id', None)
        try:
            user = DctUser.objects.get(id=id)
            auth = get_redis_conf(name=None, user=user)
            redis = RedisConf.objects.all()
            return render(request, 'change_user.html', {
                'menu': menu,
                'user_info': user,
                'auth': auth,
                'rediss': redis,
            })
        except Exception as e:
            logs.error(u"修改用户信息: id:{0},msg:{1}".format(id, e))
            return render(request, 'change_user.html', {
                'error': e
            })

    def post(self, request):
        menu = Menu(user=request.user)

        id = request.POST.get('id', None)
        password1 = request.POST.get('password1', None)
        password2 = request.POST.get('password2', None)
        email = request.POST.get('email', None)
        is_superuser = request.POST.get('is_superuser', None)

        rediss = RedisConf.objects.all()
        user = DctUser.objects.get(id=id)

        for re in rediss:
            re_id = request.POST.get(re.name, None)
            # 判断是否获取到值
            if re_id is None:
                continue

            # 值是否为空
            elif re_id == '':
                try:
                    # ''为删除权限
                    user.auths.get(redis=re.id).delete()
                except Exception as e:
                    logs.error(u"删除权限失败:user_id:{0},redis:{1},msg:{2}".format(id,re.id,e))
                continue

            pre_auth = int(re_id)  # 权限数

            # 用户所有权限
            user_redis = []
            for i in user.auths.all():
                user_redis.append(i.redis)

            # 判断用户是否拥有该redis的权限，没有就创建，有及更新
            if re.id not in user_redis:
                try:
                    pre_obj = Auth.objects.get(redis=re.id, pre_auth=pre_auth)
                except Exception as e:
                    pre_obj = Auth.objects.create(
                        redis=re.id,
                        pre_auth=pre_auth
                    )
                user.auths.add(pre_obj)
                user.save()
            else:
                if user.auths.get(redis=re.id).pre_auth != pre_auth:
                    try:
                        pre_obj = Auth.objects.get(redis=re.id, pre_auth=pre_auth)

                    except Exception as e:
                        pre_obj = Auth.objects.create(
                            redis=re.id,
                            pre_auth=pre_auth
                        )
                    finally:
                        user_pre = user.auths.remove(user.auths.get(redis=re.id))
                        user.auths.add(pre_obj)
                        user.save()

        error = ''

        try:
            user = DctUser.objects.get(id=id)

            # 是否超级用户
            if is_superuser is not None:
                user.is_staff = True
                user.is_superuser = True
            else:
                user.is_staff = False
                user.is_superuser = False

            # 修改密码
            if password1 and password2:
                if password1 == password2:
                    user.set_password(password1)
                else:
                    error = '密码不一致'

            user.email = email
            user.save()

        except Exception as e:
            error = e

        return render(request, 'change_user.html', {
            'menu': menu,
            'user_info': user,
            'error': error
        })


class AddUser(LoginRequiredMixin, View):
    def get(self, request):
        menu = Menu(user=request.user)
        redis = RedisConf.objects.all()

        return render(request, 'add_user.html', {
            'menu': menu,
            'rediss': redis,
        })

    def post(self, request):
        menu = Menu(user=request.user)

        username = request.POST.get('username', None)
        password1 = request.POST.get('password1', None)
        password2 = request.POST.get('password2', None)
        email = request.POST.get('email', None)
        is_superuser = request.POST.get('is_superuser', None)

        if username and email and password1 == password2:
            try:

                # 是否超级用户
                if is_superuser is None:
                    user = DctUser.objects.create_user(username=username, email=email, password=password1)
                else:
                    user = DctUser.objects.create_superuser(username=username, email=email, password=password1)

                # 添加权限
                rediss = RedisConf.objects.all()

                for re in rediss:
                    re_id = request.POST.get(re.name, None)
                    # 判断是否获取到值
                    if re_id is None or re_id == '':
                        continue

                    pre_auth = int(request.POST.get(re.name, None))  # 权限数
                    try:
                        auth = Auth.objects.get(redis=re.id, pre_auth=pre_auth)
                        user.auths.add(auth)
                        user.save()
                    except Exception as e:
                        auth = Auth.objects.create(redis=re.id, pre_auth=pre_auth)
                    user.auths.add(auth)
                    user.save()

                return HttpResponseRedirect(reverse("user_manage"))
            except Exception as e:
                return render(request, 'add_user.html', {
                    'menu': menu,
                    'user_error': e,
                })


class UserRegisterView(View):
    def get(self, request):
        return render(request, 'register.html', {})

    def post(self, request):
        username = request.POST.get('username', None)
        password1 = request.POST.get('password1', None)
        password2 = request.POST.get('password2', None)
        email = request.POST.get('email', None)
        data = dict(
            code=1,
            msg="",
            data=""
        )
        if username is not None and password1 == password2 and email is not None:
            try:
                user = DctUser.objects.create_user(username=username, email=email, password=password1)
                send_email("用户注册", u"用户:{0}，邮箱:{1} \n\t注册redis管理平台请分配权限".format(username, email),
                           receivers=mail_receivers)
                data["code"] = 0
                data["msg"] = "注册成功,联系管理员分配权限中。"
            except Exception as e:
                data["code"] = 1
                data["msg"] = '{0}'.format(e)
        elif password1 != password2:
            data["msg"] = "密码不一致"
        else:
            data["code"] = 1
            data["msg"] = "error"
        return JsonResponse(data=data, safe=False)


class TestView(View):
    def get(self, request):
        # redis_conf_obj = RedisConf.objects.get(
        #     name='redis2',
        # )
        #
        # user_obj = DctUser.objects.get(username='carey')
        # pre_obj = Auth.objects.create(
        #     redis=redis_conf_obj.id,
        #     pre_auth=3,
        # )
        # user_obj.auths.add(pre_obj)
        # user_obj.save()
        return JsonResponse(data=True, safe=False)
