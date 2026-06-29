# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_dropoffcenter_latitude_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='dropoffcenter',
            name='business_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='dropoffcenter',
            name='business_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('kiosk', 'Kiosk'),
                    ('shop', 'Shop'),
                    ('pharmacy', 'Pharmacy'),
                    ('petrol_station', 'Petrol Station'),
                    ('school', 'School'),
                    ('other', 'Other'),
                ],
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='dropoffcenter',
            name='materials_accepted',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='dropoffcenter',
            name='mpesa_number',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='dropoffcenter',
            name='national_id_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='dropoffcenter',
            name='national_id_photo',
            field=models.ImageField(blank=True, null=True, upload_to='host_ids/'),
        ),
        migrations.AddField(
            model_name='dropoffcenter',
            name='operating_hours_close',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dropoffcenter',
            name='operating_hours_open',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dropoffcenter',
            name='shopfront_photo',
            field=models.ImageField(blank=True, null=True, upload_to='host_shopfront/'),
        ),
        migrations.AddField(
            model_name='dropoffcenter',
            name='status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                default='pending',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[
                    ('user', 'User'),
                    ('household', 'Household'),
                    ('aggregator', 'Aggregator'),
                    ('host', 'Host'),
                    ('recycler', 'Recycler'),
                ],
                default='recycler',
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='RecyclerApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200)),
                ('contact_name', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('vehicle_info', models.TextField()),
                ('proof_document', models.FileField(upload_to='recycler_applications/')),
                ('status', models.CharField(
                    choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                    default='pending',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='recycler_application',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
        migrations.RunPython(
            lambda apps, schema_editor: apps.get_model('accounts', 'DropOffCenter').objects.filter(
                is_active=True,
            ).update(status='approved'),
            migrations.RunPython.noop,
        ),
    ]
