from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RecyclableItem, PickupRequest
from .forms import RecyclableItemForm, PickupRequestForm
from accounts.models import DropOffCenter
from django.contrib.auth.models import User

def home_view(request):
    return render(request, 'home.html')


@login_required
def dashboard_view(request):
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
    if request.user.userprofile.user_type != 'shop_owner':
        messages.error(request, 'Only shop owners can request pickups.')
        return redirect('dashboard')
    
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
            return redirect('dashboard')
    else:
        form = PickupRequestForm()
    return render(request, 'recycling/request_pickup.html', {'form': form, 'center': center})
     
@login_required
def drop_off_centers_view(request):
    centers = DropOffCenter.objects.all()
    return render(request, 'recycling/drop_off_centers.html', {'centers': centers})
