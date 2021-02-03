# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import partners.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.CharField(help_text=b'Partner organization title.', max_length=255)),
                ('url', models.CharField(help_text=b'Partner website url.', max_length=255)),
                ('image', models.ImageField(help_text=b'Partner logo image.', upload_to=partners.models.partners_assets_path, validators=[partners.models.validate_partner_image])),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
