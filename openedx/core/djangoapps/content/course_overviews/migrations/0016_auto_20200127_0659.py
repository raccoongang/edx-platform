# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0015_courseoverview_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverview',
            name='course_availability',
            field=models.TextField(default=b'Always'),
        ),
        migrations.AddField(
            model_name='courseoverview',
            name='learning_format',
            field=models.TextField(default=b'Online'),
        ),
        migrations.AddField(
            model_name='courseoverview',
            name='number_of_homeworks',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='courseoverview',
            name='number_of_lections',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='courseoverview',
            name='number_of_tests',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='courseoverview',
            name='number_of_videos',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='courseoverview',
            name='qualification_level',
            field=models.TextField(default=b'From zero'),
        ),
    ]
