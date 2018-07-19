# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_reg_form', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extrainfo',
            name='nationality_id',
            field=models.CharField(unique=True, max_length=10, verbose_name='National ID'),
        ),
    ]
