from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ShipmentForm
from .models import Shipment

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
    shipments = Shipment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tracking/dashboard.html', {'shipments': shipments})

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