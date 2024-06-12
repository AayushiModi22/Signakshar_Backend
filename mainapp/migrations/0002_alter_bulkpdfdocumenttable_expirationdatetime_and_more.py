import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulkpdfdocumenttable',
            name='expirationDateTime',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 14, 11, 29, 46, 412911, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='documenttable',
            name='expirationDateTime',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 15, 6, 47, 14, 498954, tzinfo=datetime.timezone.utc)),
        ),
    ]
