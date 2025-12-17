from django.contrib import admin
from .models import UserProfile, DropOffCenter

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone', 'points', 'total_earnings']
    list_filter = ['user_type', 'created_at']
    search_fields = ['user__username', 'phone']

@admin.register(DropOffCenter)
class DropOffCenterAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'address']