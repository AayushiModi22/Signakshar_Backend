

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emails', models.EmailField(max_length=254)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent')], default='pending', max_length=10)),
                ('docId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_lists', to='mainapp.documenttable')),
            ],
        ),
        migrations.CreateModel(
            name='ScheduledEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient_email', models.EmailField(max_length=254)),
                ('scheduled_time', models.DateTimeField()),
                ('expiration_days', models.IntegerField(default=0)),
                ('reminder_date_pm', models.DateTimeField(blank=True, null=True)),
                ('reminder_date_am', models.DateTimeField(blank=True, null=True)),
                ('sent', models.BooleanField(default=False)),
                ('doc_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_emails', to='mainapp.documenttable')),
            ],
        ),
    ]
