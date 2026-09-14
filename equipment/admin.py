from django.contrib import admin
from .models import Booking, Equipment, FaultReport, MaintenanceRecord

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_tag', 'laboratory', 'condition', 'status')
    list_filter = ('status', 'condition', 'laboratory')
    search_fields = ('name', 'asset_tag', 'category')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'user', 'start_at', 'end_at', 'status')
    list_filter = ('status',)

admin.site.register(FaultReport)
admin.site.register(MaintenanceRecord)

# Register your models here.
