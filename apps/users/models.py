# coding:utf-8
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class DctUser(AbstractUser):
	img = models.CharField(default='/static/img/default.jpg', max_length=200, verbose_name=u'用户头像')
	permission = models.IntegerField(default=1, verbose_name=u"用户权限(0:超级, 1:查看, 2:编辑,删除)")

	class Meta:
		verbose_name = u'用户管理'
		verbose_name_plural = verbose_name

	def __str__(self):
		return self.username
