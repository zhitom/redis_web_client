# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-04-13 15:37
from __future__ import unicode_literals

import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='DctUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.')], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('img', models.CharField(default='/static/img/default.jpg', max_length=200, verbose_name='\u7528\u6237\u5934\u50cf')),
            ],
            options={
                'verbose_name': '\u7528\u6237\u7ba1\u7406',
                'verbose_name_plural': '\u7528\u6237\u7ba1\u7406',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Auth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('redis', models.IntegerField(verbose_name='redis\u914d\u7f6e')),
                ('premission', models.IntegerField(default=0, verbose_name='\u6743\u9650\u7ea7\u522b')),
            ],
            options={
                'db_table': 'premission',
                'verbose_name': '\u6743\u9650',
                'verbose_name_plural': '\u6743\u9650',
            },
        ),
        migrations.CreateModel(
            name='RedisConf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField(verbose_name='\u7d22\u5f15')),
                ('name', models.CharField(max_length=1024, verbose_name='\u540d\u79f0')),
                ('host', models.CharField(max_length=1024, verbose_name='IP\u5730\u5740')),
                ('port', models.IntegerField(default=6379, verbose_name='\u7aef\u53e3')),
                ('password', models.CharField(blank=True, max_length=30, null=True, verbose_name='\u5bc6\u7801')),
                ('database', models.IntegerField(default=16, verbose_name='db\u6570')),
            ],
            options={
                'db_table': 'redis_config',
                'verbose_name': 'redis\u914d\u7f6e',
                'verbose_name_plural': 'redis\u914d\u7f6e',
            },
        ),
        migrations.AddField(
            model_name='dctuser',
            name='auths',
            field=models.ManyToManyField(blank=True, default=None, null=True, to='users.Auth'),
        ),
        migrations.AddField(
            model_name='dctuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='dctuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
