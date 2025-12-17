from django.db import models
from django.contrib.auth.models import User
from accounts.models import DropOffCenter

class RecyclableItem(models.Model):
    MATERIAL_CHOICES = [
        ('paper', 'Paper'),
        ('plastic', 'Plastic'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('collected', 'Collected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recyclables')
    material_type = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight in KG")
    description = models.TextField()
    image = models.ImageField(upload_to='recyclables/')
    drop_off_center = models.ForeignKey(DropOffCenter, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    points_earned = models.IntegerField(default=0)
    amount_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.material_type} - {self.weight}kg by {self.user.username}"
    
    def calculate_rewards(self):
        # Paper: 10 points/kg, KES 5/kg
        # Plastic: 15 points/kg, KES 8/kg
        if self.material_type == 'paper':
            self.points_earned = int(self.weight * 10)
            self.amount_earned = self.weight * 5
        elif self.material_type == 'plastic':
            self.points_earned = int(self.weight * 15)
            self.amount_earned = self.weight * 8
        self.save()


class PickupRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    drop_off_center = models.ForeignKey(DropOffCenter, on_delete=models.CASCADE)
    scheduled_date = models.DateTimeField()
    total_weight = models.DecimalField(max_digits=10, decimal_places=2)
    pickup_fee = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Pickup for {self.drop_off_center.name} - {self.scheduled_date}"