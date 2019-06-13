# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_category', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursecategory',
            name='slug',
            field=models.SlugField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coursecategorycourse',
            name='course_category',
            field=models.ForeignKey(to='course_category.CourseCategory', null=True),
        ),
    ]
