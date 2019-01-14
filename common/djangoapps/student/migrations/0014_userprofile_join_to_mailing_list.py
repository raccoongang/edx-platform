# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0013_auto_20180625_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='join_to_mailing_list',
            field=models.BooleanField(default=False),
        ),
    ]
