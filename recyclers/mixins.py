from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


class RecyclingCompanyRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not hasattr(request.user, 'recycling_company'):
            messages.error(request, 'Recycling company account required.')
            return redirect('recycler_register_step1')
        return super().dispatch(request, *args, **kwargs)

    def get_company(self):
        return self.request.user.recycling_company


class ApprovedCompanyMixin(RecyclingCompanyRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        # First, check auth + company existence via parent
        response = super().dispatch(request, *args, **kwargs)

        # FIX: Only pass through actual redirect responses (302), not every response
        if getattr(response, 'status_code', None) in (301, 302, 307, 308):
            return response

        # Now check approval and subscription status
        company = self.get_company()
        if company.status != 'approved':
            messages.warning(request, 'Your company profile is not yet approved.')
            return redirect('recycler_pending')
        if not company.subscription_active:
            messages.warning(request, 'Your subscription is inactive.')
            return redirect('recycler_pending')

        return response


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff