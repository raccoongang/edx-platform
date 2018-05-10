# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ci_program', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='enrolled_students',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='program',
            name='zoho_program_code',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
