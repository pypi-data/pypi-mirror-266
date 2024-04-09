# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('regex_match', '0002_modelrule_priority'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modelrule',
            options={'ordering': ('-priority',)},
        ),
    ]
