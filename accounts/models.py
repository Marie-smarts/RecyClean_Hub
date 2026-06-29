from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('household', 'Household'),
        ('aggregator', 'Aggregator'),
        ('host', 'Host'),
        ('recycler', 'Recycler'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='recycler')
    phone = models.CharField(max_length=15)
    address = models.TextField()
    points = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


class DropOffCenter(models.Model):
    BUSINESS_TYPE_CHOICES = [
        ('kiosk', 'Kiosk'),
        ('shop', 'Shop'),
        ('pharmacy', 'Pharmacy'),
        ('petrol_station', 'Petrol Station'),
        ('school', 'School'),
        ('other', 'Other'),
    ]
    HOST_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    business_name = models.CharField(max_length=200, blank=True)
    business_type = models.CharField(
        max_length=30,
        choices=BUSINESS_TYPE_CHOICES,
        blank=True,
    )
    operating_hours_open = models.TimeField(null=True, blank=True)
    operating_hours_close = models.TimeField(null=True, blank=True)
    materials_accepted = models.JSONField(default=list, blank=True)
    mpesa_number = models.CharField(max_length=15, blank=True)
    national_id_number = models.CharField(max_length=20, blank=True)
    national_id_photo = models.ImageField(upload_to='host_ids/', null=True, blank=True)
    shopfront_photo = models.ImageField(upload_to='host_shopfront/', null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=HOST_STATUS_CHOICES,
        default='pending',
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='WGS84 latitude for map and nearby search',
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='WGS84 longitude for map and nearby search',
    )
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='centers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def has_coordinates(self):
        return self.latitude is not None and self.longitude is not None


class DropOffHost(DropOffCenter):
    """Proxy for drop-off hosts (shop-owned centers). Same table as DropOffCenter."""

    class Meta:
        proxy = True
        verbose_name = 'drop off host'
        verbose_name_plural = 'drop off hosts'


class RecyclerApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recycler_application')
    company_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    vehicle_info = models.TextField()
    proof_document = models.FileField(upload_to='recycler_applications/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.company_name} ({self.get_status_display()})'