# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0010_auto_20170207_0458'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profession',
            field=models.CharField(default=b'und', max_length=5, db_index=True, choices=[(b'media', b'Media professional, activist, human rights defender'), (b'other', b'Other'), (b'o', b'Undisclosed')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='region',
            field=models.CharField(default=b'und', max_length=4, db_index=True, choices=[(b'afr', b'Africa'), (b'asia', b'Asia & Pacific'), (b'eur', b'Europe'), (b's_us', b'Latin / South America'), (b'n_us', b'North America'), (b'mena', b'MENA'), (b'o', b'Undisclosed')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_age',
            field=models.CharField(default=b'und', max_length=3, db_index=True, choices=[(b'20', b'< 20'), (b'40', b'20-40'), (b'64', b'41-64'), (b'65', b'65+'), (b'und', b'Undisclosed')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(default=b'o', max_length=1, db_index=True, choices=[(b'm', b'Male'), (b'f', b'Female'), (b'o', b'Other / Undisclosed')]),
        ),
    ]
