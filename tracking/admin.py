from django.contrib import admin
from .models import Shipment, ShipmentUpdate

class ShipmentUpdateInline(admin.TabularInline):
    model = ShipmentUpdate
    extra = 1  # Provides one empty row by default to quickly add a new update
    fields = ('location', 'update_message', 'timestamp')
    readonly_fields = ('timestamp',)

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('tracking_id', 'status', 'sender_name', 'receiver_name', 'origin', 'destination', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('tracking_id', 'sender_name', 'receiver_name')
    readonly_fields = ('tracking_id', 'created_at')
    inlines = [ShipmentUpdateInline]

@admin.register(ShipmentUpdate)
class ShipmentUpdateAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'location', 'update_message', 'timestamp')
    search_fields = ('shipment__tracking_id', 'location')
    list_filter = ('timestamp',)