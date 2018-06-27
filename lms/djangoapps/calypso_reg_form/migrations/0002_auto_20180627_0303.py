# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calypso_reg_form', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StateExtraInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(max_length=2, verbose_name='State', choices=[(b'AL', b'Alabama'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'ME', b'Maine'), (b'MI', b'Michigan'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'Wisconsin'), (b'WY', b'Wyoming')])),
                ('license', models.CharField(max_length=255, verbose_name='License')),
                ('extra_info', models.ForeignKey(to='calypso_reg_form.ExtraInfo')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='licenseextrainfo',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='licenseextrainfo',
            name='extra_info',
        ),
        migrations.AlterUniqueTogether(
            name='usstateextrainfo',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='usstateextrainfo',
            name='extra_info',
        ),
        migrations.DeleteModel(
            name='LicenseExtraInfo',
        ),
        migrations.DeleteModel(
            name='USStateExtraInfo',
        ),
        migrations.AlterUniqueTogether(
            name='stateextrainfo',
            unique_together=set([('extra_info', 'state')]),
        ),
    ]
