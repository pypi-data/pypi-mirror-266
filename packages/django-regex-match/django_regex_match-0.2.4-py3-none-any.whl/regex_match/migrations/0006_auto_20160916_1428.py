# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regex_match', '0005_auto_20151117_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelexception',
            name='template',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='parsermethod',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='regexrule',
            name='regex',
            field=models.TextField(),
        ),
    ]
