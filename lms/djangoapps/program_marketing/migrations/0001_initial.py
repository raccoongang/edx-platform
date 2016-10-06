# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramMarketing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('marketing_slug', models.SlugField(max_length=64)),
                ('title', models.CharField(max_length=128, blank=True)),
                ('program_id', models.PositiveIntegerField(null=True, blank=True)),
                ('description', models.TextField()),
                ('promo_video_url', models.URLField(blank=True)),
                ('promo_image_url', models.URLField(blank=True)),
            ],
        ),
    ]
