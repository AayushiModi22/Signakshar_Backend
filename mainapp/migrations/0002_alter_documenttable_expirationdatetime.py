# Generated by Django 5.0.6 on 2024-06-03 09:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documenttable',
            name='expirationDateTime',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 10, 9, 7, 19, 513057, tzinfo=datetime.timezone.utc)),
        ),
    ]
