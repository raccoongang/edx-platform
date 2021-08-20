# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0019_courseoverview_archived'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverview',
            name='eng_cert_course_name',
            field=models.TextField(default=b''),
        ),
    ]
