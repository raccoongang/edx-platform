# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ci_program', '0003_auto_20180202_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='image',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='program',
            name='video',
            field=models.URLField(null=True, blank=True),
        ),
    ]
