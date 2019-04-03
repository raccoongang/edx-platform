# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='contact_us_form',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'name')),
                ('emailid', models.CharField(max_length=255, db_index=True)),
                ('message', models.CharField(max_length=3000, null=True, blank=True)),
                ('inquiry_type', models.CharField(max_length=2, db_index=True)),
                ('phone', models.CharField(max_length=13, db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
