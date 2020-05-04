# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('student', '0008_auto_20161117_1209'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserGeneratedCertGradeData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('grade', models.CharField(max_length=255, null=True)),
                ('percent', models.FloatField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserGeneratedCertPercentData',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('course_grade', models.FloatField(null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='usergeneratedcertgradedata',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
