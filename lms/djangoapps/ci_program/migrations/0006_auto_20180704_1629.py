# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ci_program', '0005_merge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='program',
            old_name='zoho_program_code',
            new_name='program_code',
        ),
        migrations.RemoveField(
            model_name='program',
            name='number_of_modules',
        ),
        migrations.AddField(
            model_name='program',
            name='program_code_friendly_name',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='program',
            name='enrolled_students',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
