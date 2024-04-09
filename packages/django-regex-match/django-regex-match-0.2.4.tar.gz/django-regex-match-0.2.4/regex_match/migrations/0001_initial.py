# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatchingRule',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ModelRule',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('model_field', models.CharField(max_length=16)),
                ('model_field_type', models.CharField(max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Parser',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('parser_method_params', models.CharField(blank=True, max_length=16, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ParserMethod',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ExceptionParser',
            fields=[
                ('parser_ptr', models.OneToOneField(primary_key=True, parent_link=True, to='regex_match.Parser', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=32)),
            ],
            options={
                'abstract': False,
            },
            bases=('regex_match.parser',),
        ),
        migrations.CreateModel(
            name='ModelException',
            fields=[
                ('modelrule_ptr', models.OneToOneField(primary_key=True, parent_link=True, to='regex_match.ModelRule', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=32)),
                ('template', models.CharField(max_length=64)),
            ],
            options={
                'abstract': False,
            },
            bases=('regex_match.modelrule',),
        ),
        migrations.CreateModel(
            name='RegexRule',
            fields=[
                ('parser_ptr', models.OneToOneField(primary_key=True, parent_link=True, to='regex_match.Parser', auto_created=True, serialize=False)),
                ('regex', models.CharField(max_length=32)),
            ],
            options={
                'abstract': False,
            },
            bases=('regex_match.parser',),
        ),
        migrations.AlterUniqueTogether(
            name='parsermethod',
            unique_together=set([('name', 'type')]),
        ),
        migrations.AddField(
            model_name='parser',
            name='parser_method',
            field=models.ForeignKey(related_name='parsers', to='regex_match.ParserMethod'),
        ),
        migrations.AddField(
            model_name='parser',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_regex_match.parser_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='modelrule',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_regex_match.modelrule_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='matchingrule',
            name='model_rule',
            field=models.ForeignKey(related_name='matching_rules', to='regex_match.ModelRule'),
        ),
        migrations.AddField(
            model_name='regexrule',
            name='matching_rule',
            field=models.ForeignKey(related_name='regex_rules', to='regex_match.MatchingRule'),
        ),
        migrations.AddField(
            model_name='exceptionparser',
            name='model_exception',
            field=models.ForeignKey(related_name='parsers', to='regex_match.ModelException'),
        ),
    ]
