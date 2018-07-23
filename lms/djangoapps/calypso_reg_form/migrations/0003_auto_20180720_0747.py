# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calypso_reg_form', '0002_auto_20180627_0303'),
    ]

    operations = [
        migrations.AddField(
            model_name='extrainfo',
            name='usa_state',
            field=models.CharField(default=None, max_length=255, verbose_name='State'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='extrainfo',
            name='zip_code',
            field=models.CharField(default=None, max_length=255, verbose_name='Zip'),
            preserve_default=False,
        ),
    ]
