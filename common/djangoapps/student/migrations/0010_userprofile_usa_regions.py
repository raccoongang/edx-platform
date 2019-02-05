# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0009_userprofile_usa_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='usa_regions',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
