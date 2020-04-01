# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edeos', '0002_auto_20190723_0226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersociallink',
            name='platform',
            field=models.CharField(max_length=50, choices=[(b'facebook', b'Facebook'), (b'skype', b'Skype'), (b'vk', b'VK'), (b'telegram', b'Telegram')]),
        ),
        migrations.AlterField(
            model_name='usersociallink',
            name='social_link',
            field=models.CharField(max_length=64, blank=True),
        ),
    ]
