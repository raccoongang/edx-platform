# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0018_courseoverview_telegram_chat_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverview',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
