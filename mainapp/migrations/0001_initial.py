# Generated by Django 5.0.6 on 2024-06-19 05:05

import datetime
import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='otpUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('otp', models.IntegerField(max_length=6)),
                ('status', models.CharField(default='N', max_length=1)),
                ('entry_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RecipientRole',
            fields=[
                ('role_id', models.AutoField(primary_key=True, serialize=False)),
                ('role_name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('full_name', models.CharField(blank=True, max_length=300, null=True)),
                ('initial', models.CharField(blank=True, max_length=10, null=True)),
                ('stamp_img_name', models.TextField(blank=True, null=True)),
                ('stamp_enc_key', models.CharField(blank=True, max_length=255, null=True)),
                ('s3Key', models.CharField(blank=True, max_length=255, null=True)),
                ('signIn_with_google', models.CharField(blank=True, default='N', max_length=10, null=True)),
                ('profile_pic', models.TextField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BulkPdfDocumentTable',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('selectedPdfs', models.JSONField()),
                ('creationDateTime', models.DateTimeField(default=django.utils.timezone.now)),
                ('s3Key', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=100)),
                ('email_title', models.CharField(default='Hello', max_length=100)),
                ('email_msg', models.CharField(default='Hello', max_length=500)),
                ('req_type', models.CharField(default='N', max_length=1)),
                ('Schedule_type', models.CharField(default='N', max_length=1)),
                ('last_modified_date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('expirationDateTime', models.DateTimeField(default=datetime.datetime(2024, 6, 26, 5, 5, 13, 445970, tzinfo=datetime.timezone.utc))),
                ('reminderDays', models.IntegerField(default=15)),
                ('creator_id', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='positions_sent_bulkpdf', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bulk_documents_last_modified', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BulkPdfRecipientDetail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('docId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.bulkpdfdocumenttable')),
                ('roleId', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='mainapp.recipientrole')),
            ],
        ),
        migrations.CreateModel(
            name='BulkPdfPositionData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fieldName', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=50)),
                ('boxId', models.CharField(max_length=100)),
                ('pageNum', models.IntegerField()),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('width', models.FloatField()),
                ('height', models.FloatField()),
                ('signer_status', models.CharField(choices=[('Signed', 'Signed'), ('Unsigned', 'Unsigned')], max_length=100, unique=True)),
                ('reviewer_status', models.CharField(choices=[('Approved', 'Approved'), ('Declined', 'Declined')], max_length=100, unique=True)),
                ('docId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.bulkpdfdocumenttable')),
                ('bulkpdf_recipient_detail_id', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='mainapp.bulkpdfrecipientdetail')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentTable',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('pdfName', models.CharField(max_length=100)),
                ('creationDateTime', models.DateTimeField(default=django.utils.timezone.now)),
                ('size', models.IntegerField()),
                ('s3Key', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=100)),
                ('email_title', models.CharField(max_length=100)),
                ('email_msg', models.CharField(max_length=500)),
                ('req_type', models.CharField(default='N', max_length=1)),
                ('Schedule_type', models.CharField(default='N', max_length=1)),
                ('last_modified_date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('expirationDateTime', models.DateTimeField(default=datetime.datetime(2024, 6, 26, 5, 5, 13, 429564, tzinfo=datetime.timezone.utc))),
                ('reminderDays', models.IntegerField()),
                ('creator_id', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='positions_sent', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='documents_last_modified', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentRecipientDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('docId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.documenttable')),
                ('roleId', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='mainapp.recipientrole')),
            ],
        ),
        migrations.CreateModel(
            name='Initials',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('draw_img_name', models.TextField(blank=True, null=True)),
                ('draw_enc_key', models.CharField(blank=True, max_length=255, null=True)),
                ('img_name', models.TextField(blank=True, null=True)),
                ('img_enc_key', models.CharField(blank=True, max_length=255, null=True)),
                ('initial_text', models.TextField(blank=True, null=True)),
                ('initial_text_value', models.CharField(blank=True, max_length=255, null=True)),
                ('initial_text_font', models.CharField(blank=True, max_length=255, null=True)),
                ('initial_text_color', models.CharField(blank=True, max_length=255, null=True)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RecipientPositionData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fieldName', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=50)),
                ('boxId', models.CharField(max_length=100)),
                ('pageNum', models.IntegerField()),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('width', models.FloatField()),
                ('height', models.FloatField()),
                ('signer_status', models.CharField(choices=[('Signed', 'Signed'), ('Unsigned', 'Unsigned')], max_length=100)),
                ('reviewer_status', models.CharField(choices=[('Approved', 'Approved'), ('Declined', 'Declined')], max_length=100)),
                ('docId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.documenttable')),
                ('docRecipientdetails_id', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='mainapp.documentrecipientdetail')),
            ],
        ),
        migrations.CreateModel(
            name='Signature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('draw_img_name', models.TextField(blank=True, null=True)),
                ('draw_enc_key', models.CharField(blank=True, max_length=255, null=True)),
                ('img_name', models.TextField(blank=True, null=True)),
                ('img_enc_key', models.CharField(blank=True, max_length=255, null=True)),
                ('sign_text', models.TextField(blank=True, null=True)),
                ('sign_text_value', models.CharField(blank=True, max_length=255, null=True)),
                ('sign_text_font', models.CharField(blank=True, max_length=255, null=True)),
                ('sign_text_color', models.CharField(blank=True, max_length=255, null=True)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('template_id', models.AutoField(primary_key=True, serialize=False)),
                ('templateName', models.CharField(max_length=255)),
                ('createTempfile', models.CharField(max_length=255)),
                ('templateNumPages', models.IntegerField()),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TemplateRecipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.recipientrole')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='template', to='mainapp.template')),
            ],
        ),
        migrations.CreateModel(
            name='TemplateDraggedData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fieldName', models.CharField(max_length=255, null=True)),
                ('color', models.CharField(max_length=50, null=True)),
                ('recBoxid', models.CharField(max_length=255, null=True)),
                ('pageNum', models.IntegerField(null=True)),
                ('x', models.FloatField(null=True)),
                ('y', models.FloatField(null=True)),
                ('width', models.FloatField(null=True)),
                ('height', models.FloatField(null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.recipientrole')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dragged_data', to='mainapp.template')),
                ('templateRec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='template_recipient', to='mainapp.templaterecipient')),
            ],
        ),
        migrations.CreateModel(
            name='UseTemplateRecipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RecipientName', models.CharField(max_length=255)),
                ('RecipientEmail', models.EmailField(max_length=254)),
                ('dummy_name', models.CharField(max_length=255)),
                ('userSelectfile', models.CharField(max_length=255)),
                ('signer_status', models.CharField(choices=[('Signed', 'Signed'), ('Unsigned', 'Unsigned')], max_length=100)),
                ('reviewer_status', models.CharField(choices=[('Approved', 'Approved'), ('Declined', 'Declined'), ('InProgress', 'InProgress')], max_length=100)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('docid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.documenttable')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.recipientrole')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipients', to='mainapp.template')),
                ('templateRec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='temp_recipient', to='mainapp.templaterecipient')),
            ],
        ),
    ]
