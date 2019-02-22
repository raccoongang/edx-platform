# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0011_auto_20180605_0425'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverview',
            name='course_level',
            field=models.CharField(blank=True, max_length=25, verbose_name=b'Course level', choices=[(b'Introductory', b'Introductory'), (b'Intermediate', b'Intermediate'), (b'Advanced', b'Advanced')]),
        ),
        migrations.AddField(
            model_name='courseoverview',
            name='main_topic',
            field=models.CharField(max_length=256, verbose_name=b'Main topic', blank=True),
        ),
        migrations.AddField(
            model_name='courseoverview',
            name='skilltag',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='courseoverview',
            name='total_effort',
            field=models.CharField(default=b'', max_length=256, verbose_name=b'Total effort', blank=True),
        ),
    ]
