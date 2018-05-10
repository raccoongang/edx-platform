# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ci_program', '0002_auto_20180201_2134'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='effort',
            field=models.CharField(max_length=25, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='program',
            name='full_description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='program',
            name='length_of_program',
            field=models.CharField(max_length=25, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='program',
            name='number_of_modules',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
