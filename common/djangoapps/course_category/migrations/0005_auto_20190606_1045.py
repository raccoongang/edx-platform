# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0011_auto_20180605_0425'),
        ('course_category', '0004_auto_20190531_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursecategory',
            name='courses',
            field=models.ManyToManyField(to='course_overviews.CourseOverview', blank=True),
        ),
        migrations.AddField(
            model_name='coursecategory',
            name='img',
            field=models.ImageField(upload_to=b'course_category', blank=True),
        ),
        migrations.AddField(
            model_name='coursecategory',
            name='url',
            field=models.URLField(null=True, blank=True),
        ),
    ]
