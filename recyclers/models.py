from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class RecyclingCompany(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    SUBSCRIPTION_PLAN_CHOICES = [
        ('basic', 'Basic — KES 5,000 / month'),
        ('standard', 'Standard — KES 10,000 / month'),
        ('premium', 'Premium — KES 15,000 / month'),
    ]

    MATERIAL_KEYS = ['plastic', 'metal', 'paper', 'glass', 'aluminium']

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='recycling_company',
    )
    company_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100, unique=True)
    kra_pin = models.CharField(max_length=20)
    kra_pin_certificate = models.FileField(upload_to='recycler_docs/')
    nema_permit = models.FileField(upload_to='recycler_docs/', blank=True)
    website = models.URLField(blank=True)
    company_email = models.EmailField()
    facility_photo = models.ImageField(upload_to='recycler_facility/')

    physical_address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    contact_name = models.CharField(max_length=200)
    contact_title = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    contact_national_id = models.CharField(max_length=20)

    materials_accepted = models.JSONField(default=list)
    weekly_capacity_tonnes = models.FloatField()
    price_per_kg_plastic = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_per_kg_metal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_per_kg_paper = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_per_kg_glass = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_per_kg_aluminium = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    subscription_plan = models.CharField(max_length=20, choices=SUBSCRIPTION_PLAN_CHOICES)
    subscription_active = models.BooleanField(default=False)
    subscription_start = models.DateField(null=True, blank=True)
    subscription_end = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    company_code = models.CharField(max_length=20, unique=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_recycling_companies',
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'recycling companies'
        ordering = ['-submitted_at']

    def __str__(self):
        return self.company_name

    @property
    def is_approved(self):
        return self.status == 'approved'

    def price_field_for_material(self, material):
        return {
            'plastic': self.price_per_kg_plastic,
            'metal': self.price_per_kg_metal,
            'paper': self.price_per_kg_paper,
            'glass': self.price_per_kg_glass,
            'aluminium': self.price_per_kg_aluminium,
        }.get(material)

    def sync_price_table(self):
        """Push company buy prices into the platform PriceTable."""
        for material in self.MATERIAL_KEYS:
            price = self.price_field_for_material(material)
            if price is None:
                continue
            PriceTable.objects.update_or_create(
                company=self,
                material=material,
                defaults={
                    'price_per_kg': price,
                    'is_active': self.subscription_active and self.is_approved,
                },
            )

    def approve(self, admin_user):
        from .services import generate_company_code, subscription_end_date

        self.status = 'approved'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.rejection_reason = ''
        if not self.company_code:
            self.company_code = generate_company_code()
        today = timezone.now().date()
        self.subscription_active = True
        self.subscription_start = today
        self.subscription_end = subscription_end_date(today)
        self.save()
        self.sync_price_table()

    def reject(self, admin_user, reason=''):
        self.status = 'rejected'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.rejection_reason = reason
        self.subscription_active = False
        self.save()
        PriceTable.objects.filter(company=self).update(is_active=False)


class PriceTable(models.Model):
    """
    Platform price table — collection systems read active rows via get_material_price().
    """

    MATERIAL_CHOICES = [
        ('plastic', 'Plastic'),
        ('metal', 'Metal'),
        ('paper', 'Paper'),
        ('glass', 'Glass'),
        ('aluminium', 'Aluminium'),
    ]

    company = models.ForeignKey(
        RecyclingCompany,
        on_delete=models.CASCADE,
        related_name='price_rows',
    )
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['company', 'material']]
        ordering = ['material']

    def __str__(self):
        return f'{self.company.company_name} — {self.material}: KES {self.price_per_kg}/kg'


class TraceabilityRecord(models.Model):
    company = models.ForeignKey(
        RecyclingCompany,
        on_delete=models.CASCADE,
        related_name='traceability_records',
    )
    collection_log = models.ForeignKey(
        'aggregators.CollectionLog',
        on_delete=models.CASCADE,
        related_name='traceability_records',
    )
    aggregator_reference = models.CharField(max_length=30)
    host_code = models.CharField(max_length=30)
    material_type = models.CharField(max_length=20)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    recorded_at = models.DateTimeField()

    class Meta:
        ordering = ['-recorded_at']
        unique_together = [['company', 'collection_log']]

    def __str__(self):
        return f'{self.company_code_display} ← {self.aggregator_reference}'

    @property
    def company_code_display(self):
        return self.company.company_code or '—'


class SupplyPipelineEntry(models.Model):
    company = models.ForeignKey(
        RecyclingCompany,
        on_delete=models.CASCADE,
        related_name='pipeline_entries',
    )
    assignment = models.ForeignKey(
        'aggregators.AggregatorPickupAssignment',
        on_delete=models.CASCADE,
        related_name='supply_pipeline_entries',
    )
    distance_km = models.DecimalField(max_digits=8, decimal_places=2)
    is_confirmed = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['distance_km']
        unique_together = [['company', 'assignment']]
