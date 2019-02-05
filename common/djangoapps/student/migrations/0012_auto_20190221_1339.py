# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0011_remove_userprofile_usa_region'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='usa_regions',
            new_name='usa_region',
        ),
    ]
