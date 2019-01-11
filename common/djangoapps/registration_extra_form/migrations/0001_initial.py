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
                ('accepted_to_be_contacted', models.BooleanField(default=False, help_text=b'I accept to be contacted by email around Microsoft/Cloud products and Education')),
                ('interested_in', models.CharField(help_text=b'Which Microsoft product/solution are you interested in?', max_length=255, blank=True)),
                ('areas_to_support', models.CharField(help_text=b'Any specific areas Arrow could support you with?', max_length=255, blank=True)),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
