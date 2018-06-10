# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_enrollment', '0002_programaccessstatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollmentstatushistory',
            name='enrollment_type',
            field=models.IntegerField(choices=[(0, b'Enrollment'), (1, b'Un-enrollment'), (2, b'Re-enrollment'), (3, b'Upgrade')]),
        ),
    ]
