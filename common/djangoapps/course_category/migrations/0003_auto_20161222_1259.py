# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_category', '0002_auto_20161222_1257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursecategory',
            name='slug',
            field=models.SlugField(unique=True, max_length=255),
        ),
    ]
