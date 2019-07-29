# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edeos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersociallink',
            name='platform',
            field=models.CharField(max_length=50, choices=[(b'facebook', b'Facebook')]),
        ),
    ]
