# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0010_userprofile_usa_regions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='usa_region',
        ),
    ]
