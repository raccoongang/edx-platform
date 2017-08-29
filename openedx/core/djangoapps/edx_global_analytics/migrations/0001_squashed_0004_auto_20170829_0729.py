# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [(b'edx_global_analytics', '0001_initial'), (b'edx_global_analytics', '0002_tasklog'), (b'edx_global_analytics', '0003_auto_20170829_0717'), (b'edx_global_analytics', '0004_auto_20170829_0729')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessTokensStorage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('access_token', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TaskLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_last_run_datetime', models.DateTimeField()),
            ],
        ),
    ]
