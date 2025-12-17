from django.db import models
from django.contrib.auth.models import User
from recycling.models import RecyclableItem, PickupRequest

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('recycler_earning', 'Recycler Earning'),
        ('pickup_fee', 'Pickup Fee'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    mpesa_code = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    recyclable_item = models.ForeignKey(RecyclableItem, on_delete=models.SET_NULL, null=True, blank=True)
    pickup_request = models.ForeignKey(PickupRequest, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.payment_type} - KES {self.amount} - {self.status}"