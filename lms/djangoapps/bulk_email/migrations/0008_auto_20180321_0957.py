# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_email', '0007_auto_20180223_0355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseemail',
            name='from_addr',
            field=models.CharField(default='devops@raccoongang.com', max_length=255, null=True),
        ),
    ]
