# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import partners.models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='image',
            field=models.FileField(help_text=b'Partner logo image.', upload_to=partners.models.partners_assets_path, validators=[partners.models.validate_partner_image]),
        ),
    ]
