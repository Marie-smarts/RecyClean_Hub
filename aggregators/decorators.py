from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def aggregator_login_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, 'aggregatorprofile', None)
        if profile is None:
            messages.error(request, 'Aggregator account required.')
            # FIX: Redirect to registration, NOT login_redirect_url_name (which loops)
            return redirect('aggregator_register')
        if profile.verification_status != 'approved':
            messages.warning(request, 'Your aggregator account is awaiting admin verification.')
            return redirect('aggregator_pending')
        return view_func(request, *args, **kwargs)

    return wrapper