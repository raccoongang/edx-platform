# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0016_auto_20200127_0659'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverview',
            name='class_time',
            field=models.TextField(null=True),
        ),
    ]
