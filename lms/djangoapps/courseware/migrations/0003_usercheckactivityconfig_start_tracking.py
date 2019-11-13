# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('courseware', '0002_usercheckactivityconfig'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercheckactivityconfig',
            name='start_tracking',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
