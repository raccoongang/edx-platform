# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_groups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursecohort',
            name='duration',
            field=models.PositiveIntegerField(default=45),
        ),
        migrations.AddField(
            model_name='coursecohort',
            name='manual_start',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coursecohort',
            name='start_datetime',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
