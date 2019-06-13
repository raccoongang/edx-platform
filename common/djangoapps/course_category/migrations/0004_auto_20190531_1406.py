# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import openedx.core.djangoapps.xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        ('course_category', '0003_auto_20161222_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursecategory',
            name='name',
            field=models.CharField(unique=True, max_length=255, verbose_name='Category Name'),
        ),
        migrations.AlterField(
            model_name='coursecategorycourse',
            name='course_id',
            field=openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, verbose_name='Course', db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='coursecategorycourse',
            unique_together=set([('course_category', 'course_id')]),
        ),
    ]
