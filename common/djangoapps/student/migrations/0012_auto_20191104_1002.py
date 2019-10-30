# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0011_auto_20190729_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profitonomy_public_key',
            field=models.CharField(max_length=64, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='wallet_name',
            field=models.CharField(max_length=12, blank=True),
        ),
    ]
