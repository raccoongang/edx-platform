# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CourseCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(help_text=b"The 'course' part of course_keys associated with this course code, for example 'DemoX' in 'edX/DemoX/Demo_Course'.", max_length=128)),
                ('display_name', models.CharField(help_text='The display name of this course code.', max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=True)),
                ('name', models.CharField(help_text='The user-facing display name for this Program.', unique=True, max_length=255)),
                ('subtitle', models.CharField(help_text='A brief, descriptive subtitle for the Program.', max_length=255, blank=True)),
                ('marketing_slug', models.CharField(help_text='Slug used to generate links to the marketing site', max_length=255, blank=True)),
                ('number_of_modules', models.IntegerField(null=True, blank=True)),
                ('length_of_program', models.CharField(max_length=25, null=True, blank=True)),
                ('effort', models.CharField(max_length=25, null=True, blank=True)),
                ('full_description', models.TextField(null=True, blank=True)),
                ('image', models.URLField(null=True, blank=True)),
                ('video', models.URLField(null=True, blank=True)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
        ),
        migrations.CreateModel(
            name='ProgramCourseCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('position', models.IntegerField()),
                ('course_code', models.ForeignKey(to='ci_program.CourseCode')),
                ('program', models.ForeignKey(to='ci_program.Program')),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.AddField(
            model_name='coursecode',
            name='programs',
            field=models.ManyToManyField(related_name='course_codes', through='ci_program.ProgramCourseCode', to='ci_program.Program'),
        ),
    ]
