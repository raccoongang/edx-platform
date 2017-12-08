# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0003_auto_20160511_2227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditconfig',
            name='cache_ttl',
            field=models.PositiveIntegerField(default=0, help_text='\u0417\u0430\u0434\u0430\u0451\u0442\u0441\u044f \u0432 \u0441\u0435\u043a\u0443\u043d\u0434\u0430\u0445. \u0414\u043b\u044f \u0432\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u044f \u043a\u044d\u0448\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f \u0443\u043a\u0430\u0436\u0438\u0442\u0435 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435 \u0431\u043e\u043b\u044c\u0448\u0435 0.', verbose_name='\u041f\u0435\u0440\u0438\u043e\u0434 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f \u043a\u044d\u0448\u0430'),
        ),
    ]
