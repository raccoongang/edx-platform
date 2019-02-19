# -*- coding: utf-8 -*-
from django.db import migrations


def rename_state(apps, schema_editor):
    StateExtraInfo = apps.get_model('calypso_reg_form', 'StateExtraInfo')
    StateExtraInfo.objects.filter(state='WV').update(state='WI')


class Migration(migrations.Migration):

    dependencies = [
        ('calypso_reg_form', '0004_auto_20190213_0534'),
    ]

    operations = [
        migrations.RunPython(rename_state, migrations.RunPython.noop),
    ]
