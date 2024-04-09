# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regex_match', '0004_auto_20151112_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regexrule',
            name='regex',
            field=models.CharField(max_length=128),
        ),
    ]
