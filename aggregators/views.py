from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import UserProfile
from accounts.utils import username_from_email
from recycling.models import PickupRequest

from .decorators import aggregator_login_required
from .forms import (
    AggregatorRegistrationForm,
    CollectionLogForm,
    PickupStatusForm,
)
from .models import AggregatorPickupAssignment, AggregatorProfile, CollectionLog
from .services import calculate_payment_split, get_share_rates


def register_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'aggregatorprofile'):
            if request.user.aggregatorprofile.is_verified:
                return redirect('aggregator_dashboard')
            return redirect('aggregator_pending')

    if request.method == 'POST':
        form = AggregatorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                username=username_from_email(form.cleaned_data['email']),
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            full_name = f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}".strip()
            AggregatorProfile.objects.create(
                user=user,
                company_name=full_name,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['service_area'],
                service_area=form.cleaned_data['service_area'],
                national_id_number=form.cleaned_data['national_id_number'],
                national_id_photo=form.cleaned_data['national_id_photo'],
                verification_status='pending',
            )
            UserProfile.objects.create(
                user=user,
                role='aggregator',
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['service_area'],
            )
            return redirect('aggregator_register_done')
    else:
        form = AggregatorRegistrationForm()

    return render(
        request,
        'aggregators/register.html',
        {'form': form},
    )


@login_required
def pending_view(request):
    profile = getattr(request.user, 'aggregatorprofile', None)
    if profile is None:
        messages.error(request, 'No aggregator profile found.')
        return redirect('home')
    if profile.is_verified:
        return redirect('aggregator_dashboard')
    return render(request, 'aggregators/pending.html', {'profile': profile})


def register_done_view(request):
    return render(request, 'aggregators/register_done.html')


@aggregator_login_required
def dashboard_view(request):
    profile = request.user.aggregatorprofile
    assignments = profile.pickup_assignments.select_related(
        'pickup_request__drop_off_center',
    )
    active_pickups = assignments.exclude(status__in=['completed', 'cancelled']).count()
    completed_pickups = assignments.filter(status='completed').count()
    recent_collections = profile.collection_logs.select_related('drop_off_center')[:5]
    recent_assignments = assignments[:5]

    return render(
        request,
        'aggregator/dashboard.html',
        {
            'profile': profile,
            'active_pickups': active_pickups,
            'completed_pickups': completed_pickups,
            'recent_collections': recent_collections,
            'recent_assignments': recent_assignments,
        },
    )


@aggregator_login_required
def pickups_view(request):
    profile = request.user.aggregatorprofile
    my_assignments = profile.pickup_assignments.select_related(
        'pickup_request__drop_off_center',
    ).order_by('-assigned_at')

    assigned_ids = AggregatorPickupAssignment.objects.values_list('pickup_request_id', flat=True)
    available_pickups = PickupRequest.objects.filter(
        status='pending',
    ).exclude(
        id__in=assigned_ids,
    ).select_related('drop_off_center')

    return render(
        request,
        'aggregators/pickups.html',
        {
            'my_assignments': my_assignments,
            'available_pickups': available_pickups,
        },
    )


@aggregator_login_required
def accept_pickup_view(request, pk):
    pickup = get_object_or_404(PickupRequest, pk=pk, status='pending')
    if hasattr(pickup, 'aggregator_assignment'):
        messages.error(request, 'This pickup is already assigned.')
        return redirect('aggregator_pickups')

    profile = request.user.aggregatorprofile
    AggregatorPickupAssignment.objects.create(
        pickup_request=pickup,
        aggregator=profile,
    )
    pickup.status = 'scheduled'
    pickup.save(update_fields=['status'])
    messages.success(request, f'Pickup for {pickup.drop_off_center.name} assigned to you.')
    return redirect('aggregator_pickups')


@aggregator_login_required
def pickup_detail_view(request, pk):
    assignment = get_object_or_404(
        AggregatorPickupAssignment,
        pk=pk,
        aggregator=request.user.aggregatorprofile,
    )

    if request.method == 'POST':
        form = PickupStatusForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            pickup = assignment.pickup_request
            if assignment.status == 'in_progress' and pickup.status == 'scheduled':
                pickup.status = 'scheduled'
                pickup.save(update_fields=['status'])
            elif assignment.status == 'cancelled':
                pickup.status = 'cancelled'
                pickup.save(update_fields=['status'])
            messages.success(request, 'Pickup updated.')
            return redirect('aggregator_pickup_detail', pk=assignment.pk)
    else:
        form = PickupStatusForm(instance=assignment)

    has_collection = hasattr(assignment, 'collection_log')
    return render(
        request,
        'aggregators/pickup_detail.html',
        {
            'assignment': assignment,
            'form': form,
            'has_collection': has_collection,
        },
    )


@aggregator_login_required
def log_collection_view(request, assignment_pk):
    assignment = get_object_or_404(
        AggregatorPickupAssignment,
        pk=assignment_pk,
        aggregator=request.user.aggregatorprofile,
    )

    if assignment.status == 'completed' or hasattr(assignment, 'collection_log'):
        messages.info(request, 'Collection already logged for this pickup.')
        return redirect('aggregator_pickup_detail', pk=assignment.pk)

    pickup = assignment.pickup_request
    initial_gross = pickup.pickup_fee or (pickup.total_weight * Decimal('50'))

    if request.method == 'POST':
        form = CollectionLogForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.aggregator = assignment.aggregator
            collection.assignment = assignment
            collection.drop_off_center = pickup.drop_off_center
            collection.save()

            assignment.status = 'completed'
            assignment.completed_at = timezone.now()
            assignment.save(update_fields=['status', 'completed_at'])

            pickup.status = 'completed'
            pickup.completed_at = timezone.now()
            pickup.save(update_fields=['status', 'completed_at'])

            messages.success(request, 'Collection logged and payment split recorded.')
            return redirect('aggregator_collection_detail', pk=collection.pk)
    else:
        form = CollectionLogForm(
            initial={'gross_amount': initial_gross, 'weight_kg': pickup.total_weight},
        )

    gross_preview = form.data.get('gross_amount') or initial_gross
    try:
        gross_preview = Decimal(gross_preview)
    except Exception:
        gross_preview = initial_gross
    platform, aggregator_amt, host = calculate_payment_split(gross_preview)

    return render(
        request,
        'aggregators/log_collection.html',
        {
            'form': form,
            'assignment': assignment,
            'preview': {
                'platform': platform,
                'aggregator': aggregator_amt,
                'host': host,
            },
        },
    )


@aggregator_login_required
def collection_detail_view(request, pk):
    collection = get_object_or_404(
        CollectionLog,
        pk=pk,
        aggregator=request.user.aggregatorprofile,
    )
    return render(request, 'aggregators/collection_detail.html', {'collection': collection})


@aggregator_login_required
def collections_list_view(request):
    collections = request.user.aggregatorprofile.collection_logs.select_related(
        'drop_off_center',
    )
    return render(request, 'aggregators/collections.html', {'collections': collections})


@user_passes_test(lambda u: u.is_staff)
@login_required
def admin_verify_list_view(request):
    pending = AggregatorProfile.objects.filter(verification_status='pending')
    return render(request, 'aggregators/admin_verify.html', {'pending_aggregators': pending})


@user_passes_test(lambda u: u.is_staff)
@login_required
def admin_verify_action_view(request, pk, action):
    if request.method != 'POST':
        return redirect('aggregator_admin_verify')
    profile = get_object_or_404(AggregatorProfile, pk=pk)
    if action == 'approve':
        profile.approve(request.user)
        messages.success(request, f'Approved {profile.company_name}.')
    elif action == 'reject':
        reason = request.POST.get('reason', '')
        profile.reject(request.user, reason)
        messages.warning(request, f'Rejected {profile.company_name}.')
    return redirect('aggregator_admin_verify')
