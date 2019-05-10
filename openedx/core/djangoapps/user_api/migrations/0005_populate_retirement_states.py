# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from openedx.core.djangoapps.user_api.management.commands.populate_retirement_states import Command


class Migration(migrations.Migration):

    dependencies = [
        ('user_api', '0004_userretirementpartnerreportingstatus'),
    ]

    operations = [
        migrations.RunPython(Command().handle)
    ]
