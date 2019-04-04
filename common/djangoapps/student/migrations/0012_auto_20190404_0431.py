# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0011_auto_20190325_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(default=b'u', max_length=1, db_index=True, choices=[(b'f', b'Female'), (b'g', b'Gender Nonconforming'), (b'm', b'Male'), (b'o', b'Other'), (b'u', b'Undisclosed')]),
        ),
    ]
