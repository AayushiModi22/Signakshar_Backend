import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_alter_bulkpdfdocumenttable_expirationdatetime_and_more'),
    ]

    operations = [
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
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 17, 12, 17, 59, 13023, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='documenttable',
            name='expirationDateTime',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 17, 12, 17, 58, 997485, tzinfo=datetime.timezone.utc)),
        ),
    ]
