# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_email', '0006_auto_20170627_0755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseemail',
            name='from_addr',
            field=models.CharField(default='courses@ifnmu.edu.ua', max_length=255, null=True),
        ),
    ]
