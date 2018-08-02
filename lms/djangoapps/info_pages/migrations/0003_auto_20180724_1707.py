# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info_pages', '0002_auto_20170613_1028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='infopage',
            name='page',
            field=models.CharField(unique=True, max_length=50, choices=[(b'about.html', 'about'), (b'privacy.html', 'privacy'), (b'tos.html', 'tos'), (b'contact.html', 'contact'), (b'honor.html', 'honor'), (b'what_is_verified_cert.html', 'verified-certificate'), (b'faq.html', 'help'), (b'blog.html', 'blog'), (b'press.html', 'press'), ('why_firebrand.html', 'why-firebrand'), (b'donate.html', 'donate'), (b'sitemap.xml.html', b'sitemap_xml')]),
        ),
    ]
