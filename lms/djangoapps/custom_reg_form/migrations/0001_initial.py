# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtraInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('street', models.CharField(max_length=255, verbose_name='Street')),
                ('street_number', models.CharField(max_length=50, verbose_name='Street Number')),
                ('place', models.CharField(max_length=255, verbose_name='Place')),
                ('zip_code', models.CharField(max_length=50, verbose_name='Zip Code')),
                ('phone', models.CharField(max_length=20, null=True, verbose_name='Phone', blank=True)),
                ('date_of_birth', models.DateField(null=True, verbose_name='Date of Birth', blank=True)),
                ('user_role', models.CharField(default=b'ST', max_length=2, verbose_name='User Role', choices=[(b'ST', 'Student'), (b'IN', 'Instructor')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
