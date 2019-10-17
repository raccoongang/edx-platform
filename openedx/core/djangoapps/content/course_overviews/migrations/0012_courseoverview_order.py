# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0011_auto_20180605_0425'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverview',
            name='order',
            field=models.IntegerField(null=True),
        ),
    ]
