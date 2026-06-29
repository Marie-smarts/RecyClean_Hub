# Generated manually for aggregators app

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('recycling', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AggregatorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('vehicle_info', models.CharField(blank=True, max_length=200)),
                ('verification_status', models.CharField(
                    choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                    default='pending',
                    max_length=20,
                )),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('rejection_reason', models.TextField(blank=True)),
                ('total_collections', models.PositiveIntegerField(default=0)),
                ('total_earnings', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='aggregatorprofile',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('verified_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='verified_aggregators',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AggregatorPickupAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[
                        ('assigned', 'Assigned'),
                        ('in_progress', 'In Progress'),
                        ('completed', 'Completed'),
                        ('cancelled', 'Cancelled'),
                    ],
                    default='assigned',
                    max_length=20,
                )),
                ('notes', models.TextField(blank=True)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('aggregator', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='pickup_assignments',
                    to='aggregators.aggregatorprofile',
                )),
                ('pickup_request', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='aggregator_assignment',
                    to='recycling.pickuprequest',
                )),
            ],
            options={
                'ordering': ['-assigned_at'],
            },
        ),
        migrations.CreateModel(
            name='CollectionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material_type', models.CharField(
                    choices=[('paper', 'Paper'), ('plastic', 'Plastic'), ('mixed', 'Mixed')],
                    default='mixed',
                    max_length=20,
                )),
                ('weight_kg', models.DecimalField(decimal_places=2, max_digits=10)),
                ('gross_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('platform_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('aggregator_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('host_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('notes', models.TextField(blank=True)),
                ('collected_at', models.DateTimeField(auto_now_add=True)),
                ('aggregator', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='collection_logs',
                    to='aggregators.aggregatorprofile',
                )),
                ('assignment', models.OneToOneField(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='collection_log',
                    to='aggregators.aggregatorpickupassignment',
                )),
                ('drop_off_center', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='accounts.dropoffcenter',
                )),
            ],
            options={
                'ordering': ['-collected_at'],
            },
        ),
    ]
