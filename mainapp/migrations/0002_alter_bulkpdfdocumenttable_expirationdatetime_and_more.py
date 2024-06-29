# Generated by Django 5.0.6 on 2024-06-28 11:41

import datetime
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulkpdfdocumenttable',
            name='expirationDateTime',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 5, 11, 41, 18, 51188, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='documenttable',
            name='expirationDateTime',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 5, 11, 41, 18, 51188, tzinfo=datetime.timezone.utc)),
        ),
        migrations.CreateModel(
            name='ApiLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.CharField(max_length=255)),
                ('view_name', models.CharField(max_length=255)),
                ('method', models.CharField(max_length=255)),
                ('log_level', models.CharField(max_length=255)),
                ('log_message', models.CharField(max_length=255)),
                ('json_payload', models.TextField(blank=True, null=True)),
                ('entry_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('loggedin_user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
