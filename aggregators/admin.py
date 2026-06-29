from django.contrib import admin

from .models import AggregatorPickupAssignment, AggregatorProfile, CollectionLog


@admin.action(description='Approve selected aggregators')
def approve_aggregators(modeladmin, request, queryset):
    for profile in queryset:
        profile.approve(request.user)


@admin.register(AggregatorProfile)
class AggregatorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'phone', 'verification_status', 'is_verified', 'created_at']
    list_filter = ['verification_status']
    list_editable = ['verification_status']
    search_fields = ['company_name', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'verified_at', 'is_verified']
    actions = [approve_aggregators]


@admin.register(AggregatorPickupAssignment)
class AggregatorPickupAssignmentAdmin(admin.ModelAdmin):
    list_display = ['pickup_request', 'aggregator', 'status', 'assigned_at', 'completed_at']
    list_filter = ['status', 'assigned_at']
    search_fields = ['aggregator__company_name', 'pickup_request__drop_off_center__name']
    raw_id_fields = ['pickup_request', 'aggregator']


@admin.register(CollectionLog)
class CollectionLogAdmin(admin.ModelAdmin):
    list_display = [
        'aggregator',
        'drop_off_center',
        'weight_kg',
        'gross_amount',
        'aggregator_amount',
        'host_amount',
        'platform_amount',
        'collected_at',
    ]
    list_filter = ['material_type', 'collected_at']
    search_fields = ['aggregator__company_name', 'drop_off_center__name']
    readonly_fields = [
        'platform_amount',
        'aggregator_amount',
        'host_amount',
        'collected_at',
    ]
