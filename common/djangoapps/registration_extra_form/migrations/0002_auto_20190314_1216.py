# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('registration_extra_form', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='extrainfo',
            name='phone',
            field=models.CharField(blank=True, max_length=15, verbose_name=b'Phone number', validators=[django.core.validators.RegexValidator(regex=b'^\\d{9,15}$', message=b'The phone number must be from 9 to 15 digits inclusively.')]),
        ),
        migrations.AlterField(
            model_name='extrainfo',
            name='accepted_to_be_contacted',
            field=models.BooleanField(verbose_name=b'I accept to be contacted by email around Microsoft/Cloud products and Education'),
        ),
        migrations.AlterField(
            model_name='extrainfo',
            name='areas_to_support',
            field=models.CharField(max_length=255, verbose_name=b'Any specific areas Arrow could support you with?', blank=True),
        ),
        migrations.AlterField(
            model_name='extrainfo',
            name='interested_in',
            field=models.CharField(max_length=255, verbose_name=b'Which Microsoft product/solution are you interested in?', blank=True),
        ),
    ]
