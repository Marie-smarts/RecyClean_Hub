# Generated manually for recyclers app

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('aggregators', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RecyclingCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200)),
                ('registration_number', models.CharField(max_length=100, unique=True)),
                ('kra_pin', models.CharField(max_length=20)),
                ('kra_pin_certificate', models.FileField(upload_to='recycler_docs/')),
                ('nema_permit', models.FileField(blank=True, upload_to='recycler_docs/')),
                ('website', models.URLField(blank=True)),
                ('company_email', models.EmailField(max_length=254)),
                ('facility_photo', models.ImageField(upload_to='recycler_facility/')),
                ('physical_address', models.TextField()),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('contact_name', models.CharField(max_length=200)),
                ('contact_title', models.CharField(max_length=100)),
                ('contact_phone', models.CharField(max_length=15)),
                ('contact_national_id', models.CharField(max_length=20)),
                ('materials_accepted', models.JSONField(default=list)),
                ('weekly_capacity_tonnes', models.FloatField()),
                ('price_per_kg_plastic', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('price_per_kg_metal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('price_per_kg_paper', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('price_per_kg_glass', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('price_per_kg_aluminium', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('subscription_plan', models.CharField(
                    choices=[
                        ('basic', 'Basic — KES 5,000 / month'),
                        ('standard', 'Standard — KES 10,000 / month'),
                        ('premium', 'Premium — KES 15,000 / month'),
                    ],
                    max_length=20,
                )),
                ('subscription_active', models.BooleanField(default=False)),
                ('subscription_start', models.DateField(blank=True, null=True)),
                ('subscription_end', models.DateField(blank=True, null=True)),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('approved', 'Approved'),
                        ('rejected', 'Rejected'),
                    ],
                    default='pending',
                    max_length=20,
                )),
                ('company_code', models.CharField(blank=True, max_length=20, unique=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('rejection_reason', models.TextField(blank=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='recycling_company',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('verified_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='verified_recycling_companies',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name_plural': 'recycling companies',
                'ordering': ['-submitted_at'],
            },
        ),
        migrations.CreateModel(
            name='PriceTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material', models.CharField(
                    choices=[
                        ('plastic', 'Plastic'),
                        ('metal', 'Metal'),
                        ('paper', 'Paper'),
                        ('glass', 'Glass'),
                        ('aluminium', 'Aluminium'),
                    ],
                    max_length=20,
                )),
                ('price_per_kg', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='price_rows',
                    to='recyclers.recyclingcompany',
                )),
            ],
            options={
                'ordering': ['material'],
                'unique_together': {('company', 'material')},
            },
        ),
        migrations.CreateModel(
            name='TraceabilityRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aggregator_reference', models.CharField(max_length=30)),
                ('host_code', models.CharField(max_length=30)),
                ('material_type', models.CharField(max_length=20)),
                ('weight_kg', models.DecimalField(decimal_places=2, max_digits=10)),
                ('gross_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('recorded_at', models.DateTimeField()),
                ('collection_log', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='traceability_records',
                    to='aggregators.collectionlog',
                )),
                ('company', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='traceability_records',
                    to='recyclers.recyclingcompany',
                )),
            ],
            options={
                'ordering': ['-recorded_at'],
                'unique_together': {('company', 'collection_log')},
            },
        ),
        migrations.CreateModel(
            name='SupplyPipelineEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance_km', models.DecimalField(decimal_places=2, max_digits=8)),
                ('is_confirmed', models.BooleanField(default=True)),
                ('notes', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assignment', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='supply_pipeline_entries',
                    to='aggregators.aggregatorpickupassignment',
                )),
                ('company', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='pipeline_entries',
                    to='recyclers.recyclingcompany',
                )),
            ],
            options={
                'ordering': ['distance_km'],
                'unique_together': {('company', 'assignment')},
            },
        ),
    ]
