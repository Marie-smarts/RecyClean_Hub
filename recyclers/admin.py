from django.contrib import admin

from .models import PriceTable, RecyclingCompany, SupplyPipelineEntry, TraceabilityRecord


class PriceTableInline(admin.TabularInline):
    model = PriceTable
    extra = 0
    readonly_fields = ['updated_at']


@admin.register(RecyclingCompany)
class RecyclingCompanyAdmin(admin.ModelAdmin):
    list_display = [
        'company_name',
        'company_code',
        'status',
        'subscription_plan',
        'subscription_active',
        'submitted_at',
    ]
    list_filter = ['status', 'subscription_plan', 'subscription_active']
    search_fields = ['company_name', 'registration_number', 'company_code', 'kra_pin']
    readonly_fields = ['submitted_at', 'verified_at', 'company_code']
    inlines = [PriceTableInline]


@admin.register(PriceTable)
class PriceTableAdmin(admin.ModelAdmin):
    list_display = ['company', 'material', 'price_per_kg', 'is_active', 'updated_at']
    list_filter = ['material', 'is_active']


@admin.register(TraceabilityRecord)
class TraceabilityRecordAdmin(admin.ModelAdmin):
    list_display = [
        'company',
        'aggregator_reference',
        'host_code',
        'material_type',
        'weight_kg',
        'recorded_at',
    ]
    list_filter = ['material_type']


@admin.register(SupplyPipelineEntry)
class SupplyPipelineEntryAdmin(admin.ModelAdmin):
    list_display = ['company', 'assignment', 'distance_km', 'is_confirmed', 'created_at']
