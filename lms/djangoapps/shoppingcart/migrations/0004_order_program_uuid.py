# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingcart', '0003_auto_20151217_0958'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='program_uuid',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]
