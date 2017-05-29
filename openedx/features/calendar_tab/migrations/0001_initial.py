# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CourseCalendar',
            fields=[
                ('course_id', models.CharField(max_length=255)),
                ('calendar_id', models.CharField(max_length=255, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='CourseCalendarEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_id', models.CharField(max_length=255)),
                ('edx_user', models.CharField(max_length=255)),
                ('course_calendar', models.ForeignKey(to='calendar_tab.CourseCalendar')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='coursecalendar',
            unique_together=set([('course_id', 'calendar_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='coursecalendarevent',
            unique_together=set([('course_calendar', 'event_id')]),
        ),
    ]
