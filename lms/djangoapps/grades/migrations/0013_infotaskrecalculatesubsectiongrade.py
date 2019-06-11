# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import openedx.core.djangoapps.xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        ('grades', '0012_computegradessetting'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfoTaskRecalculateSubsectionGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('course_id', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255)),
                ('user_id', models.IntegerField()),
                ('task_id', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=12, choices=[(b'start', b'start'), (b'error', b'error'), (b'success', b'success')])),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
