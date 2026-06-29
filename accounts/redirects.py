"""Post-login redirect targets by user role."""

from .models import DropOffCenter


def login_redirect_url_name(user):
    """Return the URL name for the dashboard (or gate) matching this user's role."""
    profile = getattr(user, 'userprofile', None)
    if profile is None:
        return 'home'

    role = profile.role
    if role in ('user', 'household'):
        return 'household_dashboard'

    if role == 'recycler':
        application = getattr(user, 'recycler_application', None)
        if application and application.status in ('pending', 'rejected'):
            return 'register_recycler_done'
        if application and application.status == 'approved' and hasattr(user, 'recycling_company'):
            return 'recycling_company_dashboard'
        if application and application.status == 'approved':
            return 'recycler_dashboard'
        if application is None:
            return 'recycler_dashboard'
        return 'recycler_register_step1'

    if role == 'host':
        center = DropOffCenter.objects.filter(owner=user).first()
        if center and center.status == 'pending':
            return 'register_host_done'
        return 'host_dashboard'

    if role == 'aggregator':
        aggregator_profile = getattr(user, 'aggregatorprofile', None)
        if aggregator_profile and aggregator_profile.verification_status == 'pending':
            return 'aggregator_register_done'
        if aggregator_profile and not aggregator_profile.is_verified:
            return 'aggregator_pending'
        # FIX: If no aggregator profile exists, don't return 'aggregator_dashboard'
        # (that creates a loop with @aggregator_login_required).
        if aggregator_profile is None:
            return 'aggregator_register'
        return 'aggregator_dashboard'

    return 'home'