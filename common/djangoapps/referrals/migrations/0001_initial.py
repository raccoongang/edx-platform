# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import openedx.core.djangoapps.xmodule_django.models

import referrals.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Referrals',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_id', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, db_index=True, null=True)),
                ('hashkey', models.CharField(default=referrals.utils.hashkey_generator, unique=True, max_length=32)),
                ('type', models.CharField(max_length=10, default=b'student_signup')),
                ('client_id', models.CharField(max_length=10)),
                ('status', models.CharField(default=b'active', max_length=10, choices=[(b'active', b'active'), (b'inactive', b'inactive')])),
                ('created', models.DateTimeField(db_index=True, auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
