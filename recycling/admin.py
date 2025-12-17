from django.contrib import admin
from .models import RecyclableItem, PickupRequest

@admin.register(RecyclableItem)
class RecyclableItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'material_type', 'weight', 'status', 'points_earned', 'amount_earned', 'submitted_at']
    list_filter = ['status', 'material_type', 'submitted_at']
    search_fields = ['user__username', 'description']
    actions = ['approve_items', 'reject_items']
    
    def approve_items(self, request, queryset):
        for item in queryset:
            if item.status == 'pending':
                item.status = 'approved'
                item.calculate_rewards()
                # Update user profile
                profile = item.user.userprofile
                profile.points += item.points_earned
                profile.total_earnings += float(item.amount_earned)
                profile.save()
        self.message_user(request, f"{queryset.count()} items approved")
    
    def reject_items(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} items rejected")

@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = ['drop_off_center', 'scheduled_date', 'total_weight', 'pickup_fee', 'status']
    list_filter = ['status', 'scheduled_date']
    search_fields = ['drop_off_center__name']