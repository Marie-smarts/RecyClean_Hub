from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from accounts.models import DropOffCenter
from recycling.models import PickupRequest

from .services import calculate_payment_split


class AggregatorProfile(models.Model):
    VERIFICATION_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='aggregatorprofile')
    company_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    vehicle_info = models.CharField(max_length=200, blank=True)
    national_id_number = models.CharField(max_length=20, blank=True)
    national_id_photo = models.ImageField(upload_to='aggregator_ids/', null=True, blank=True)
    service_area = models.TextField(blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default='pending',
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_aggregators',
    )
    rejection_reason = models.TextField(blank=True)
    total_collections = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.company_name} ({self.user.username})'

    @property
    def is_verified(self):
        return self.verification_status == 'approved'

    def approve(self, admin_user):
        self.verification_status = 'approved'
        self.verified_at = timezone.now()
        self.verified_by = admin_user
        self.rejection_reason = ''
        self.save(update_fields=[
            'verification_status',
            'verified_at',
            'verified_by',
            'rejection_reason',
        ])

    def reject(self, admin_user, reason=''):
        self.verification_status = 'rejected'
        self.verified_at = timezone.now()
        self.verified_by = admin_user
        self.rejection_reason = reason
        self.save(update_fields=[
            'verification_status',
            'verified_at',
            'verified_by',
            'rejection_reason',
        ])


class AggregatorPickupAssignment(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    pickup_request = models.OneToOneField(
        PickupRequest,
        on_delete=models.CASCADE,
        related_name='aggregator_assignment',
    )
    aggregator = models.ForeignKey(
        AggregatorProfile,
        on_delete=models.CASCADE,
        related_name='pickup_assignments',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    notes = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.aggregator} → {self.pickup_request}'


class CollectionLog(models.Model):
    MATERIAL_CHOICES = [
        ('paper', 'Paper'),
        ('plastic', 'Plastic'),
        ('mixed', 'Mixed'),
    ]

    aggregator = models.ForeignKey(
        AggregatorProfile,
        on_delete=models.CASCADE,
        related_name='collection_logs',
    )
    assignment = models.OneToOneField(
        AggregatorPickupAssignment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collection_log',
    )
    drop_off_center = models.ForeignKey(DropOffCenter, on_delete=models.CASCADE)
    material_type = models.CharField(max_length=20, choices=MATERIAL_CHOICES, default='mixed')
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    platform_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    aggregator_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    host_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-collected_at']

    def __str__(self):
        return f'Collection {self.weight_kg}kg @ {self.drop_off_center.name}'

    def apply_payment_split(self):
        platform, aggregator, host = calculate_payment_split(self.gross_amount)
        self.platform_amount = platform
        self.aggregator_amount = aggregator
        self.host_amount = host

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        self.apply_payment_split()
        super().save(*args, **kwargs)

        if is_new:
            self.aggregator.total_collections += 1
            self.aggregator.total_earnings += Decimal(self.aggregator_amount)
            self.aggregator.save(update_fields=['total_collections', 'total_earnings'])

            host_profile = self.drop_off_center.owner.userprofile
            host_profile.total_earnings += Decimal(self.host_amount)
            host_profile.save(update_fields=['total_earnings'])
