# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ci_program', '0002_auto_20180313_1318'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnrollmentStatusHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('registered', models.BooleanField()),
                ('enrollment_type', models.IntegerField(choices=[(0, b'Enrollment'), (1, b'Un-enrollment'), (2, b'Re-enrollment')])),
                ('enrolled', models.BooleanField()),
                ('email_sent', models.BooleanField()),
                ('enrollment_attempt', models.DateTimeField(auto_now_add=True)),
                ('program', models.ForeignKey(to='ci_program.Program')),
                ('student', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        )
    ]
