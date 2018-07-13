# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0014_courseoverview_certificate_available_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseoverview',
            name='_pre_requisite_courses_json',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='advertised_start',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='announcement',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='catalog_visibility',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='cert_name_long',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='cert_name_short',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='certificates_display_behavior',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='course_image_url',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='course_video_url',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='days_early_for_beta',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='effort',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='end_of_course_survey_url',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='enrollment_domain',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='enrollment_end',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='enrollment_start',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='lowest_passing_grade',
            field=models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='max_student_enrollments_allowed',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='short_description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='courseoverview',
            name='social_sharing_url',
            field=models.TextField(null=True, blank=True),
        ),
    ]
