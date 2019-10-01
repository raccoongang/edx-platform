# -*- coding: utf-8 -*-
# Created by Nikolay Borovenskiy (nikolay.borovenskiy@raccoongang.com)
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations
from django.db.models import Count, Min

UNIQUE_TOGETHER_FIELDS = ('cohort', 'user')


def remove_duplicates(apps, schema_editor):
    """
    Remove duplicate objects in case when there are two fields cohort and user to compare.
    """
    CohortAssigment = apps.get_model('instructor', 'CohortAssigment')
    duplicates = (
        CohortAssigment.objects.values(*UNIQUE_TOGETHER_FIELDS)
            .order_by()
            .annotate(min_id=Min('id'), count_id=Count('id'))
            .filter(count_id__gt=1)
    )

    for duplicate in duplicates:
        (
            CohortAssigment.objects
                .filter(**{x: duplicate[x] for x in UNIQUE_TOGETHER_FIELDS})
                .exclude(id=duplicate['min_id'])
                .delete()
        )


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course_groups', '0003_auto_20170609_1455'),
        ('instructor', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_duplicates),
        migrations.AlterUniqueTogether(
            name='cohortassigment',
            unique_together=UNIQUE_TOGETHER_FIELDS,
        ),
    ]
