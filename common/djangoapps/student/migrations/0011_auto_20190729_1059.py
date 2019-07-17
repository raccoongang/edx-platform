# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0010_auto_20170207_0458'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='mobytize_id',
            field=models.CharField(max_length=32, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mobytize_token',
            field=models.CharField(max_length=64, blank=True),
        ),
    ]
