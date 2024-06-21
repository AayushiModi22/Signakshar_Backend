# Generated by Django 5.0.6 on 2024-06-21 08:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='initials',
            name='initial_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='initials',
            name='initial_text_color',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='initials',
            name='initial_text_font',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='initials',
            name='initial_text_value',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='signature',
            name='sign_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='signature',
            name='sign_text_color',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='signature',
            name='sign_text_font',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='signature',
            name='sign_text_value',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='bulkpdfdocumenttable',
            name='expirationDateTime',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 28, 8, 4, 23, 988763, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='documenttable',
            name='expirationDateTime',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 28, 8, 4, 23, 987669, tzinfo=datetime.timezone.utc)),
        ),
    ]