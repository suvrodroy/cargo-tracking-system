import random
import string
from django.db import models
from django.contrib.auth.models import User

class Shipment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        IN_TRANSIT = 'In Transit', 'In Transit'
        OUT_FOR_DELIVERY = 'Out for Delivery', 'Out for Delivery'
        DELIVERED = 'Delivered', 'Delivered'

    # Link each shipment to the user who created it
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipments')
    
    # Cargo details
    tracking_id = models.CharField(max_length=20, unique=True, blank=True)
    sender_name = models.CharField(max_length=255)
    receiver_name = models.CharField(max_length=255)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    
    # New status field
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Override the save method to auto-generate a tracking ID if it doesn't exist."""
        if not self.tracking_id:
            while True:
                random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                new_id = f"CRG-{random_chars}"
                
                if not Shipment.objects.filter(tracking_id=new_id).exists():
                    self.tracking_id = new_id
                    break
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_id} - {self.status}"


class ShipmentUpdate(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='updates')
    update_message = models.CharField(max_length=255, help_text="e.g., 'Arrived at sorting facility'")
    location = models.CharField(max_length=255, help_text="e.g., 'Chicago, IL'")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']  # Ensure we fetch the most recent updates first

    def __str__(self):
        return f"Update for {self.shipment.tracking_id} at {self.location}"