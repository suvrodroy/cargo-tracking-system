import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class Shipment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        IN_TRANSIT = 'In Transit', 'In Transit'
        OUT_FOR_DELIVERY = 'Out for Delivery', 'Out for Delivery'
        DELIVERED = 'Delivered', 'Delivered'

    class PackageTypeChoices(models.TextChoices):
        DOCUMENT = 'Document', 'Document'
        ELECTRONICS = 'Electronics', 'Electronics'
        CLOTHING = 'Clothing', 'Clothing'
        FOOD = 'Food', 'Food'
        FRAGILE = 'Fragile', 'Fragile'
        OTHER = 'Other', 'Other'

    class PriorityChoices(models.TextChoices):
        STANDARD = 'Standard', 'Standard'
        EXPRESS = 'Express', 'Express'
        URGENT = 'Urgent', 'Urgent'

    # Link each shipment to the user who created it
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipments')
    
    # Cargo details
    tracking_id = models.CharField(max_length=20, unique=True, blank=True)
    sender_name = models.CharField(max_length=255)
    receiver_name = models.CharField(max_length=255)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    
    # Package Information
    package_type = models.CharField(
        max_length=20,
        choices=PackageTypeChoices.choices,
        default=PackageTypeChoices.OTHER
    )
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)

    # Delivery Information
    priority = models.CharField(
        max_length=20,
        choices=PriorityChoices.choices,
        default=PriorityChoices.STANDARD
    )
    estimated_delivery_date = models.DateField(null=True, blank=True)

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

    @property
    def current_location(self):
        """Returns the location from the latest shipment update, or origin if no updates exist."""
        latest_update = self.updates.exclude(location='').first() # type: ignore
        if latest_update and latest_update.location.strip():
            return latest_update.location
        return self.origin

    @property
    def current_coordinates(self):
        """Returns the latitude and longitude of the latest shipment update."""
        latest_update = self.updates.exclude(location='').first() # type: ignore
        if latest_update and latest_update.latitude and latest_update.longitude:
            return {'lat': latest_update.latitude, 'lng': latest_update.longitude}
        return None

    def __str__(self):
        return f"{self.tracking_id} - {self.status}"


class ShipmentUpdate(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='updates')
    update_message = models.CharField(max_length=255, help_text="e.g., 'Arrived at sorting facility'")
    location = models.CharField(max_length=255, help_text="e.g., 'Chicago, IL'")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']  # Ensure we fetch the most recent updates first

    def save(self, *args, **kwargs):
        """Geocode the location string to latitude and longitude before saving."""
        # Only geocode if the location has changed or lat/lng are missing
        if self.location and (self.latitude is None or self.longitude is None):
            try:
                import requests
                import urllib3
                # Disable the insecure request warning since we are intentionally bypassing SSL verification
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                url = "http://geocoding-api.open-meteo.com/v1/search"
                params = {'name': self.location, 'count': 1, 'format': 'json'}
                
                # We use Open-Meteo because their TLS configuration is highly compatible with Conda's OpenSSL
                response = requests.get(url, params=params, verify=False, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data and len(data['results']) > 0:
                        self.latitude = float(data['results'][0]['latitude'])
                        self.longitude = float(data['results'][0]['longitude'])
            except Exception as e:
                # If geocoding fails (e.g., network error), we gracefully skip it 
                # so it doesn't break the application saving process.
                print(f"Geocoding failed for {self.location}: {e}")
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Update for {self.shipment.tracking_id} at {self.location}"