from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserProfileForm, DropOffCenterForm
from .models import UserProfile, DropOffCenter

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                user_type=form.cleaned_data['user_type'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                profile_image=form.cleaned_data.get('profile_image')
            )
            login(request, user)
            messages.success(request, f'Welcome {user.first_name}!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'accounts/profile.html', {'form': form})


def drop_off_centers_view(request):
    centers = DropOffCenter.objects.filter(is_active=True)
    return render(request, 'recycling/drop_off_centers.html', {'centers': centers})


@login_required
def my_center_view(request):
    if request.user.userprofile.user_type != 'shop_owner':
        messages.error(request, 'Only shop owners can access this.')
        return redirect('dashboard')
    
    try:
        center = DropOffCenter.objects.get(owner=request.user)
    except DropOffCenter.DoesNotExist:
        center = None
    
    if request.method == 'POST':
        form = DropOffCenterForm(request.POST, request.FILES, instance=center)
        if form.is_valid():
            center = form.save(commit=False)
            center.owner = request.user
            center.save()
            messages.success(request, 'Center updated!')
            return redirect('my_center')
    else:
        form = DropOffCenterForm(instance=center) if center else DropOffCenterForm()
    
    return render(request, 'accounts/my_center.html', {'form': form, 'center': center})