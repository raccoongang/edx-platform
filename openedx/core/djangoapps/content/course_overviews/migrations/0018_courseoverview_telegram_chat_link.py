# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0017_courseoverview_class_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverview',
            name='telegram_chat_link',
            field=models.TextField(default=b'https://t.me/mama_edu'),
        ),
    ]
