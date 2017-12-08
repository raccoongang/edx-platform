# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_admin', '0006_catalog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apiaccessrequest',
            name='reason',
            field=models.TextField(help_text='\u041e\u0441\u043d\u043e\u0432\u0430\u043d\u0438\u0435 \u0434\u043b\u044f \u0434\u043e\u0441\u0442\u0443\u043f\u0430 \u043a API \u0434\u0430\u043d\u043d\u043e\u0433\u043e \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f.'),
        ),
        migrations.AlterField(
            model_name='apiaccessrequest',
            name='status',
            field=models.CharField(default=b'pending', help_text='\u0421\u0442\u0430\u0442\u0443\u0441 \u044d\u0442\u043e\u0433\u043e \u0437\u0430\u043f\u0440\u043e\u0441\u0430 API', max_length=255, db_index=True, choices=[(b'pending', '\u041e\u0436\u0438\u0434\u0430\u043d\u0438\u0435'), (b'denied', '\u041e\u0442\u043a\u0430\u0437\u0430\u043d\u043e'), (b'approved', '\u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u043e')]),
        ),
        migrations.AlterField(
            model_name='apiaccessrequest',
            name='website',
            field=models.URLField(help_text='URL \u0432\u0435\u0431-\u0441\u0430\u0439\u0442\u0430, \u0441\u0432\u044f\u0437\u0430\u043d\u043d\u043e\u0433\u043e \u0441 \u044d\u0442\u0438\u043c \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u043c API.'),
        ),
        migrations.AlterField(
            model_name='historicalapiaccessrequest',
            name='reason',
            field=models.TextField(help_text='\u041e\u0441\u043d\u043e\u0432\u0430\u043d\u0438\u0435 \u0434\u043b\u044f \u0434\u043e\u0441\u0442\u0443\u043f\u0430 \u043a API \u0434\u0430\u043d\u043d\u043e\u0433\u043e \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f.'),
        ),
        migrations.AlterField(
            model_name='historicalapiaccessrequest',
            name='status',
            field=models.CharField(default=b'pending', help_text='\u0421\u0442\u0430\u0442\u0443\u0441 \u044d\u0442\u043e\u0433\u043e \u0437\u0430\u043f\u0440\u043e\u0441\u0430 API', max_length=255, db_index=True, choices=[(b'pending', '\u041e\u0436\u0438\u0434\u0430\u043d\u0438\u0435'), (b'denied', '\u041e\u0442\u043a\u0430\u0437\u0430\u043d\u043e'), (b'approved', '\u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u043e')]),
        ),
        migrations.AlterField(
            model_name='historicalapiaccessrequest',
            name='website',
            field=models.URLField(help_text='URL \u0432\u0435\u0431-\u0441\u0430\u0439\u0442\u0430, \u0441\u0432\u044f\u0437\u0430\u043d\u043d\u043e\u0433\u043e \u0441 \u044d\u0442\u0438\u043c \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u043c API.'),
        ),
    ]
