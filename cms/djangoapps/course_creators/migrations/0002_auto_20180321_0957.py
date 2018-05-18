# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('course_creators', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursecreator',
            name='note',
            field=models.CharField(help_text='\u0645\u0644\u0627\u062d\u0638\u0627\u062a \u0627\u062e\u062a\u064a\u0627\u0631\u064a\u0629 \u062d\u0648\u0644 \u0647\u0630\u0627 \u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645 (\u0644\u0645\u0627\u0630\u0627 \u0645\u062b\u0644\u064b\u0627 \u0631\u064f\u0641\u0636 \u0637\u0644\u0628 \u0627\u0644\u062f\u062e\u0648\u0644 \u0644\u0625\u0646\u0634\u0627\u0621 \u0645\u0633\u0627\u0642)', max_length=512, blank=True),
        ),
        migrations.AlterField(
            model_name='coursecreator',
            name='state',
            field=models.CharField(default=b'unrequested', help_text='\u0627\u0644\u062d\u0627\u0644\u0629 \u0627\u0644\u062d\u0627\u0644\u064a\u0629 \u0644\u0645\u064f\u0646\u0634\u0626 \u0627\u0644\u0645\u0633\u0627\u0642 ', max_length=24, choices=[(b'unrequested', '\u063a\u064a\u0631 \u0645\u0637\u0644\u0648\u0628'), (b'pending', '\u0642\u064a\u062f \u0627\u0644\u0627\u0646\u062a\u0638\u0627\u0631'), (b'granted', '\u0645\u0645\u0646\u0648\u062d'), (b'denied', '\u0645\u0631\u0641\u0648\u0636')]),
        ),
        migrations.AlterField(
            model_name='coursecreator',
            name='state_changed',
            field=models.DateTimeField(help_text='\u062a\u0627\u0631\u064a\u062e \u0622\u062e\u0631 \u062a\u062d\u062f\u064a\u062b \u0644\u0644\u062d\u0627\u0644\u0629', verbose_name=b'state last updated', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='coursecreator',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, help_text='\u0645\u0633\u062a\u062e\u062f\u0645 \u0646\u0638\u0627\u0645 \u0627\u0633\u062a\u0648\u062f\u064a\u0648 Studio'),
        ),
    ]
