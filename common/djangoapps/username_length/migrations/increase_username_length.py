# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import validators
from django.db import migrations, models

from openedx.core.djangoapps.user_api.accounts import USERNAME_MAX_LENGTH


class Migration(migrations.Migration):

    def __init__(self, name, app_label):
        # overriding application operated upon
        super(Migration, self).__init__(name, 'auth')

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='User',
            name='username',
            field=models.CharField(
                help_text='Required. {} characters or fewer. Letters, digits and @/./+/-/_ only.'.format(USERNAME_MAX_LENGTH),
                unique=True,
                max_length=USERNAME_MAX_LENGTH,
                verbose_name='username',
                validators=[validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')]),
        ),
    ]
