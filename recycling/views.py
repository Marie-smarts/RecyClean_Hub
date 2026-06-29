from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from accounts.geo import haversine_km, parse_coordinate
from accounts.models import DropOffCenter, DropOffHost
from .forms import PickupRequestForm, RecyclableItemForm
from .models import PickupRequest, RecyclableItem

def home_view(request):
    return render(request, 'home.html')

@login_required
def dashboard_view(request):
    # If user is a recycler, send them to the PROPER company dashboard
    if request.user.userprofile.role == 'recycler':
        return redirect('recycling_company_dashboard')
    
    # If user is a host, send them to host dashboard
    if request.user.userprofile.role == 'host':
        return redirect('host_dashboard')
    
    # If user is an aggregator, send them to aggregator dashboard
    if request.user.userprofile.role == 'aggregator':
        return redirect('aggregator_dashboard')
    
    # ONLY household users get this dashboard
    total_items = RecyclableItem.objects.filter(user=request.user).count()
    approved_items = RecyclableItem.objects.filter(user=request.user, status='approved').count()
    pending_items = RecyclableItem.objects.filter(user=request.user, status='pending').count()
    recent_items = RecyclableItem.objects.filter(user=request.user)[:5]
    
    all_users = User.objects.filter(is_active=True).order_by('-userprofile__points')
    user_rank = list(all_users).index(request.user) + 1 if request.user in all_users else 0

    context = {
        'total_items': total_items,
        'approved_items': approved_items,
        'pending_items': pending_items,
        'recent_items': recent_items,
        'user_rank': user_rank,
    }
    return render(request, 'recycling/dashboard.html', context)


@login_required
def submit_recyclable_view(request):
    if request.method == 'POST':
        form = RecyclableItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, 'Item submitted for review!')
            return redirect('my_recyclables')
    else:
        form = RecyclableItemForm()
    return render(request, 'recycling/submit_recyclable.html', {'form': form})


@login_required
def my_recyclables_view(request):
    items = RecyclableItem.objects.filter(user=request.user)
    return render(request, 'recycling/my_recyclables.html', {'items': items})


@login_required
def edit_recyclable_view(request, pk):
    item = get_object_or_404(RecyclableItem, pk=pk, user=request.user)
    if item.status != 'pending':
        messages.error(request, 'Only pending items can be edited.')
        return redirect('my_recyclables')
    
    if request.method == 'POST':
        form = RecyclableItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated!')
            return redirect('my_recyclables')
    else:
        form = RecyclableItemForm(instance=item)
    return render(request, 'recycling/edit_recyclable.html', {'form': form, 'item': item})


@login_required
def delete_recyclable_view(request, pk):
    item = get_object_or_404(RecyclableItem, pk=pk, user=request.user)
    if item.status != 'pending':
        messages.error(request, 'Only pending items can be deleted.')
        return redirect('my_recyclables')
    
    item.delete()
    messages.success(request, 'Item deleted!')
    return redirect('my_recyclables')


def leaderboard_view(request):
    leaderboard = User.objects.filter(is_active=True).select_related('userprofile').order_by('-userprofile__points')[:50]
    user_rank = 0
    if request.user.is_authenticated:
        all_users = list(User.objects.filter(is_active=True).order_by('-userprofile__points'))
        user_rank = all_users.index(request.user) + 1 if request.user in all_users else 0
    
    return render(request, 'recycling/leaderboard.html', {'leaderboard': leaderboard, 'user_rank': user_rank})


@login_required
def request_pickup_view(request):
    if request.user.userprofile.role != 'host':
        messages.error(request, 'Only hosts can request pickups.')
        from accounts.redirects import login_redirect_url_name
        return redirect(login_redirect_url_name(request.user))
    
    try:
        center = DropOffCenter.objects.get(owner=request.user)
    except DropOffCenter.DoesNotExist:
        messages.error(request, 'Create your center first.')
        return redirect('my_center')
    
    if request.method == 'POST':
        form = PickupRequestForm(request.POST)
        if form.is_valid():
            pickup = form.save(commit=False)
            pickup.drop_off_center = center
            pickup.pickup_fee = pickup.total_weight * 50
            pickup.save()
            messages.success(request, 'Pickup requested!')
            return redirect('host_dashboard')
    else:
        form = PickupRequestForm()
    return render(request, 'recycling/request_pickup.html', {'form': form, 'center': center})
     
@login_required
def drop_off_centers_view(request):
    centers = DropOffHost.objects.filter(is_active=True)
    return render(request, 'recycling/drop_off_centers.html', {'centers': centers})


@require_GET
def nearby_hosts_api(request):
    """
    JSON list of active drop-off hosts within radius_km of (lat, lon).
    Query params: lat, lon, radius (km, default 25), limit (default 50).
    """
    try:
        lat = parse_coordinate(request.GET.get('lat'), 'lat')
        lon = parse_coordinate(request.GET.get('lon'), 'lon')
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)

    try:
        radius_km = float(request.GET.get('radius', 25))
        if radius_km <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({'error': 'radius must be a positive number (km).'}, status=400)

    try:
        limit = int(request.GET.get('limit', 50))
        limit = max(1, min(limit, 100))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'limit must be an integer between 1 and 100.'}, status=400)

    hosts_with_distance = []
    queryset = DropOffHost.objects.filter(
        is_active=True,
        latitude__isnull=False,
        longitude__isnull=False,
    )

    for host in queryset:
        host_lat = float(host.latitude)
        host_lon = float(host.longitude)
        distance_km = haversine_km(lat, lon, host_lat, host_lon)
        if distance_km <= radius_km:
            hosts_with_distance.append((distance_km, host))

    hosts_with_distance.sort(key=lambda item: item[0])
    hosts_with_distance = hosts_with_distance[:limit]

    results = []
    for distance_km, host in hosts_with_distance:
        image_url = host.image.url if host.image else None
        results.append(
            {
                'id': host.id,
                'name': host.name,
                'address': host.address,
                'phone': host.phone,
                'latitude': float(host.latitude),
                'longitude': float(host.longitude),
                'distance_km': round(distance_km, 2),
                'is_active': host.is_active,
                'image_url': request.build_absolute_uri(image_url) if image_url else None,
                'owner_name': host.owner.get_full_name() or host.owner.username,
            }
        )

    return JsonResponse(
        {
            'query': {'lat': lat, 'lon': lon, 'radius_km': radius_km},
            'count': len(results),
            'hosts': results,
        }
    )


@login_required
def centers_map_view(request):
    return render(
        request,
        'recycling/centers_map.html',
        {
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
            'default_lat': Decimal('-1.2921'),
            'default_lon': Decimal('36.8219'),
        },
    )
