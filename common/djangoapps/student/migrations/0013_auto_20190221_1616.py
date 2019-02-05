# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0012_auto_20190221_1339'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='usa_region',
            new_name='usa_regions',
        ),
    ]
