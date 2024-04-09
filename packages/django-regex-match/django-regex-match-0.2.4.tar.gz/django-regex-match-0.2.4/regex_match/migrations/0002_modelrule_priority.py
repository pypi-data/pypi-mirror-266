# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regex_match', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelrule',
            name='priority',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
