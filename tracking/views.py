from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ShipmentForm
from .models import Shipment, ShipmentUpdate

# --- Public Views ---

def public_index(request):
    return render(request, 'tracking/index.html')

def track_shipment(request):
    tracking_id = request.GET.get('tracking_id', '').strip()
    shipment = None
    error_message = None
    
    if tracking_id:
        shipment = Shipment.objects.filter(tracking_id=tracking_id).first()
        if not shipment:
            error_message = "No shipment found with that Tracking ID. Please check the number and try again."
            
    return render(request, 'tracking/track_shipment.html', {
        'shipment': shipment,
        'tracking_id': tracking_id,
        'error_message': error_message
    })

# --- Authenticated Views ---

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'tracking/register.html', {'form': form})

@login_required
def dashboard(request):
    user_shipments = Shipment.objects.filter(user=request.user)
    shipments = user_shipments.order_by('-created_at')
    
    # Calculate oversized stats
    total_shipments = user_shipments.count()
    in_transit_count = user_shipments.filter(status=Shipment.StatusChoices.IN_TRANSIT).count()
    delivered_count = user_shipments.filter(status=Shipment.StatusChoices.DELIVERED).count()
    
    # Fetch live activity feed (last 6 updates across all user's shipments)
    recent_updates = ShipmentUpdate.objects.filter(
        shipment__in=user_shipments
    ).select_related('shipment').order_by('-timestamp')[:6]
    
    return render(request, 'tracking/dashboard.html', {
        'shipments': shipments,
        'total_shipments': total_shipments,
        'in_transit_count': in_transit_count,
        'delivered_count': delivered_count,
        'recent_updates': recent_updates
    })

@login_required
def create_shipment(request):
    if request.method == 'POST':
        form = ShipmentForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.user = request.user
            shipment.save()
            return redirect('dashboard')
    else:
        form = ShipmentForm()
    return render(request, 'tracking/create_shipment.html', {'form': form})

@login_required
def shipment_detail(request, tracking_id):
    shipment = get_object_or_404(Shipment, tracking_id=tracking_id, user=request.user)
    return render(request, 'tracking/shipment_detail.html', {'shipment': shipment})