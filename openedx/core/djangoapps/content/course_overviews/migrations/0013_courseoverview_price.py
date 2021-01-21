# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0012_auto_20190225_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverview',
            name='price',
            field=models.IntegerField(default=0),
        ),
    ]
