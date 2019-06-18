# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0011_auto_20180605_0425'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='Category Name')),
                ('description', models.TextField(null=True, blank=True)),
                ('img', models.ImageField(upload_to=b'course_category', blank=True)),
                ('enabled', models.BooleanField(default=True)),
                ('slug', models.SlugField(unique=True, max_length=255)),
                ('url', models.URLField(null=True, blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('courses', models.ManyToManyField(to='course_overviews.CourseOverview')),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='course_category.CourseCategory', null=True)),
            ],
            options={
                'verbose_name_plural': 'Course Categories',
            },
        ),
    ]
