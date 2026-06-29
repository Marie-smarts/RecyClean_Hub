from django.contrib import admin
from django.contrib import messages

from .models import DropOffCenter, DropOffHost, RecyclerApplication, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'points', 'total_earnings']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'phone']


@admin.register(DropOffCenter)
class DropOffCenterAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'phone', 'latitude', 'longitude', 'is_active', 'created_at']
    list_filter = ['status', 'is_active', 'created_at']
    search_fields = ['name', 'address', 'business_name']
    list_editable = ['status', 'is_active']


@admin.register(DropOffHost)
class DropOffHostAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'owner', 'business_type', 'status', 'phone', 'created_at']
    list_filter = ['status', 'business_type', 'created_at']
    search_fields = ['business_name', 'name', 'owner__username']
    list_editable = ['status']


@admin.register(RecyclerApplication)
class RecyclerApplicationAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'contact_name', 'user', 'phone', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['company_name', 'contact_name', 'user__username', 'user__email', 'phone']
    readonly_fields = ['created_at']
    list_editable = ['status']
    actions = ['approve_applications', 'reject_applications']

    @admin.action(description='Approve selected applications')
    def approve_applications(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} application(s) approved.', messages.SUCCESS)

    @admin.action(description='Reject selected applications')
    def reject_applications(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} application(s) rejected.', messages.WARNING)