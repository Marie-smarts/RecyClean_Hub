from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import (
    DropOffCenterForm,
    HostRegistrationForm,
    HouseholdUserRegistrationForm,
    RecyclerPartnerRegistrationForm,
    UserProfileForm,
    UserRegistrationForm,
)
from .models import DropOffCenter, DropOffHost, RecyclerApplication, UserProfile
from .redirects import login_redirect_url_name
from .utils import username_from_email
from recycling.models import PickupRequest, RecyclableItem


def register_view(request):
    """Role selection landing page at /accounts/register/."""
    return render(request, 'accounts/register_select.html')


def register_user_view(request):
    if request.user.is_authenticated:
        return redirect(login_redirect_url_name(request.user))

    if request.method == 'POST':
        form = HouseholdUserRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=username_from_email(form.cleaned_data['email']),
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            UserProfile.objects.create(
                user=user,
                role='user',
                phone=form.cleaned_data['phone'],
                address='',
            )
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}!')
            return redirect('household_dashboard')
    else:
        form = HouseholdUserRegistrationForm()

    return render(request, 'accounts/register_user.html', {'form': form})


def register_host_view(request):
    if request.user.is_authenticated:
        return redirect(login_redirect_url_name(request.user))

    if request.method == 'POST':
        form = HostRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                username=username_from_email(form.cleaned_data['email']),
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            UserProfile.objects.create(
                user=user,
                role='host',
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['physical_address'],
            )
            DropOffHost.objects.create(
                owner=user,
                name=form.cleaned_data['business_name'],
                business_name=form.cleaned_data['business_name'],
                address=form.cleaned_data['physical_address'],
                phone=form.cleaned_data['phone'],
                business_type=form.cleaned_data['business_type'],
                operating_hours_open=form.cleaned_data['operating_hours_open'],
                operating_hours_close=form.cleaned_data['operating_hours_close'],
                materials_accepted=list(form.cleaned_data['materials_accepted']),
                mpesa_number=form.cleaned_data['mpesa_number'],
                national_id_number=form.cleaned_data['national_id_number'],
                national_id_photo=form.cleaned_data['national_id_photo'],
                shopfront_photo=form.cleaned_data['shopfront_photo'],
                image=form.cleaned_data['shopfront_photo'],
                status='pending',
                is_active=False,
            )
            return redirect('register_host_done')
    else:
        form = HostRegistrationForm()

    return render(request, 'accounts/register_host.html', {'form': form})


def register_host_done_view(request):
    return render(request, 'accounts/register_host_done.html')


def register_recycler_view(request):
    if request.user.is_authenticated:
        return redirect(login_redirect_url_name(request.user))

    if request.method == 'POST':
        form = RecyclerPartnerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                username=username_from_email(form.cleaned_data['email']),
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['contact_name'].split()[0][:30],
                last_name=' '.join(form.cleaned_data['contact_name'].split()[1:])[:150] or 'Partner',
            )
            UserProfile.objects.create(
                user=user,
                role='recycler',
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['physical_address'],
            )
            RecyclerApplication.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                contact_name=form.cleaned_data['contact_name'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['physical_address'],
                vehicle_info=form.cleaned_data['vehicle_info'],
                proof_document=form.cleaned_data['proof_document'],
                status='pending',
            )
            return redirect('register_recycler_done')
    else:
        form = RecyclerPartnerRegistrationForm()

    return render(request, 'accounts/register_recycler.html', {'form': form})


def register_recycler_done_view(request):
    return render(request, 'accounts/register_recycler_done.html')


def legacy_register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                profile_image=form.cleaned_data.get('profile_image')
            )
            login(request, user)
            messages.success(request, f'Welcome {user.first_name}!')
            return redirect(login_redirect_url_name(user))
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect(login_redirect_url_name(request.user))
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect(login_redirect_url_name(user))
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
    if request.user.userprofile.role != 'host':
        messages.error(request, 'Only hosts can access this.')
        return redirect(login_redirect_url_name(request.user))
    
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


@login_required
def household_dashboard_view(request):
    if request.user.userprofile.role not in ('user', 'household'):
        return redirect(login_redirect_url_name(request.user))
    from accounts.models import DropOffCenter
    centers_count = DropOffCenter.objects.filter(is_active=True).count()
    return render(
        request,
        'household/dashboard.html',
        {'centers_count': centers_count},
    )


@login_required
def host_dashboard_view(request):
    if request.user.userprofile.role != 'host':
        return redirect(login_redirect_url_name(request.user))

    try:
        center = DropOffCenter.objects.get(owner=request.user)
    except DropOffCenter.DoesNotExist:
        center = None

    pickup_qs = PickupRequest.objects.filter(drop_off_center=center) if center else PickupRequest.objects.none()
    pending_pickups = pickup_qs.filter(status='pending').count()
    scheduled_pickups = pickup_qs.filter(status='scheduled').count()
    completed_pickups = pickup_qs.filter(status='completed').count()
    recent_pickups = pickup_qs.order_by('-created_at')[:5]

    return render(
        request,
        'host/dashboard.html',
        {
            'center': center,
            'pending_pickups': pending_pickups,
            'scheduled_pickups': scheduled_pickups,
            'completed_pickups': completed_pickups,
            'recent_pickups': recent_pickups,
        },
    )