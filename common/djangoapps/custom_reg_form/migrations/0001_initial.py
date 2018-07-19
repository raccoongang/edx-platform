# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name = 'ExtraInfo',
            fields = [
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mobile', models.CharField(max_length=9, null=True, verbose_name='Mobile Number', blank=True)),
                ('nationality_id', models.CharField(max_length=10, verbose_name='National ID')),
                ('date_of_birth_day', models.PositiveIntegerField(validators=[
                    django.core.validators.MaxValueValidator(30),
                    django.core.validators.MinValueValidator(1)])),
                ('date_of_birth_month', models.PositiveIntegerField(validators=[
                    django.core.validators.MaxValueValidator(12),
                    django.core.validators.MinValueValidator(1)])),
                ('date_of_birth_year', models.PositiveIntegerField()),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
