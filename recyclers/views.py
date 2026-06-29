import csv
import json
import uuid
from collections import defaultdict
from decimal import Decimal

from django.contrib import messages
from django.core.files.storage import default_storage
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, TemplateView, View

from accounts.models import UserProfile
from aggregators.models import AggregatorProfile

from .forms import (
    AdminRejectForm,
    RecyclerRegistrationStep1Form,
    RecyclerRegistrationStep2Form,
    RecyclerRegistrationStep3Form,
    subscription_plan_context,
)
from .mixins import ApprovedCompanyMixin, RecyclingCompanyRequiredMixin, StaffRequiredMixin
from .models import PriceTable, RecyclingCompany, TraceabilityRecord
from .services import (
    aggregator_reference,
    refresh_supply_pipeline,
    send_registration_emails,
    send_welcome_email,
    subscription_plan_amount,
    SOURCING_RADIUS_KM,
)

SESSION_KEY = 'recycler_registration'


class RegistrationSessionMixin:
    def get_session_data(self):
        return self.request.session.get(SESSION_KEY, {})

    def save_session_data(self, data):
        current = self.request.session.get(SESSION_KEY, {})
        current.update(data)
        self.request.session[SESSION_KEY] = current
        self.request.session.modified = True


class RegisterStep1View(RegistrationSessionMixin, FormView):
    template_name = 'recyclers/register_step1.html'
    form_class = RecyclerRegistrationStep1Form

    def get_context_data(self, **kwargs):
        from django.conf import settings

        ctx = super().get_context_data(**kwargs)
        ctx['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        return ctx

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'recycling_company'):
            company = request.user.recycling_company
            if company.is_approved:
                return redirect('recycling_company_dashboard')
            return redirect('recycler_pending')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return self.get_session_data()

    def form_valid(self, form):
        data = {}
        for k, v in form.cleaned_data.items():
            if k in form.files:
                continue
            if isinstance(v, Decimal):
                data[k] = str(v)
            else:
                data[k] = v

        file_paths = {}
        for key in ('kra_pin_certificate', 'nema_permit', 'facility_photo'):
            upload = self.request.FILES.get(key)
            if upload:
                path = default_storage.save(
                    f'recycler_reg/{uuid.uuid4().hex}_{upload.name}',
                    upload,
                )
                file_paths[key] = path
        if 'kra_pin_certificate' not in file_paths:
            form.add_error('kra_pin_certificate', 'This field is required.')
            return self.form_invalid(form)
        if 'facility_photo' not in file_paths:
            form.add_error('facility_photo', 'This field is required.')
            return self.form_invalid(form)
        data['file_paths'] = file_paths
        self.save_session_data(data)
        return redirect('recycler_register_step2')


class RegisterStep2View(RegistrationSessionMixin, FormView):
    template_name = 'recyclers/register_step2.html'
    form_class = RecyclerRegistrationStep2Form

    def dispatch(self, request, *args, **kwargs):
        if not self.get_session_data():
            return redirect('recycler_register_step1')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(subscription_plan_context())
        return ctx

    def get_initial(self):
        data = self.get_session_data()
        if 'materials_accepted' in data and isinstance(data['materials_accepted'], str):
            data['materials_accepted'] = json.loads(data['materials_accepted'])
        return data

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        for k, v in data.items():
            if isinstance(v, Decimal):
                data[k] = str(v)
        data['materials_accepted'] = json.dumps(data['materials_accepted'])
        self.save_session_data(data)
        return redirect('recycler_register_step3')


class RegisterStep3View(RegistrationSessionMixin, FormView):
    template_name = 'recyclers/register_step3.html'
    form_class = RecyclerRegistrationStep3Form
    success_url = reverse_lazy('recycler_pending')

    def dispatch(self, request, *args, **kwargs):
        if not self.get_session_data().get('company_name'):
            return redirect('recycler_register_step1')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['review'] = self.get_session_data()
        ctx.update(subscription_plan_context())
        return ctx

    def form_valid(self, form):
        session_data = self.get_session_data()
        user = form.save()
        user.email = form.cleaned_data['email']
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()

        materials = session_data.get('materials_accepted', '[]')
        if isinstance(materials, str):
            materials = json.loads(materials)

        company = RecyclingCompany(
            user=user,
            company_name=session_data['company_name'],
            registration_number=session_data['registration_number'],
            kra_pin=session_data['kra_pin'],
            website=session_data.get('website', ''),
            company_email=session_data['company_email'],
            physical_address=session_data['physical_address'],
            latitude=session_data['latitude'],
            longitude=session_data['longitude'],
            contact_name=session_data['contact_name'],
            contact_title=session_data['contact_title'],
            contact_phone=session_data['contact_phone'],
            contact_national_id=session_data['contact_national_id'],
            materials_accepted=materials,
            weekly_capacity_tonnes=session_data['weekly_capacity_tonnes'],
            price_per_kg_plastic=session_data['price_per_kg_plastic'],
            price_per_kg_metal=session_data['price_per_kg_metal'],
            price_per_kg_paper=session_data['price_per_kg_paper'],
            price_per_kg_glass=session_data['price_per_kg_glass'],
            price_per_kg_aluminium=session_data['price_per_kg_aluminium'],
            subscription_plan=session_data['subscription_plan'],
        )

        # FIX: Generate unique company code
        company.company_code = f'RC{uuid.uuid4().hex[:6].upper()}'

        file_paths = session_data.get('file_paths', {})
        for field, path in file_paths.items():
            with default_storage.open(path) as stored:
                getattr(company, field).save(path.split('/')[-1], stored, save=False)

        company.save()
        company.sync_price_table()

        UserProfile.objects.create(
            user=user,
            role='recycler',
            phone=session_data['contact_phone'],
            address=session_data['physical_address'],
        )

        send_registration_emails(company)
        login(self.request, user)
        
        # SAFE DELETE - only delete if key exists
        if SESSION_KEY in self.request.session:
            del self.request.session[SESSION_KEY]
        
        messages.success(
            self.request,
            'Application submitted. Check your email for confirmation.',
        )
        return super().form_valid(form)


class PendingView(RecyclingCompanyRequiredMixin, TemplateView):
    template_name = 'recyclers/pending.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['company'] = self.get_company()
        return ctx


class DashboardView(ApprovedCompanyMixin, TemplateView):
    template_name = 'recyclers/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        company = self.get_company()
        refresh_supply_pipeline(company)

        pipeline = company.pipeline_entries.select_related(
            'assignment__pickup_request__drop_off_center',
            'assignment__aggregator',
        )[:20]

        traceability = company.traceability_records.all()[:25]

        records = company.traceability_records.all()
        weekly_volume = defaultdict(lambda: defaultdict(float))
        for rec in records:
            week = rec.recorded_at.strftime('%Y-W%W')
            weekly_volume[week][rec.material_type] += float(rec.weight_kg)

        aggregator_perf = (
            records.values('aggregator_reference')
            .annotate(total_kg=Sum('weight_kg'), trips=Count('id'))
            .order_by('-total_kg')[:10]
        )

        directory = []
        for profile in AggregatorProfile.objects.filter(
            verification_status='approved',
        ).select_related('user')[:15]:
            directory.append({
                'profile': profile,
                'reference': aggregator_reference(profile),
            })

        ctx.update({
            'company': company,
            'pipeline': pipeline,
            'traceability': traceability,
            'weekly_volume_json': json.dumps(weekly_volume),
            'aggregator_perf': aggregator_perf,
            'directory': directory[:15],
            'plan_amount': subscription_plan_amount(company.subscription_plan),
            'sourcing_radius': SOURCING_RADIUS_KM,
        })
        return ctx


class AggregatorDirectoryView(ApprovedCompanyMixin, TemplateView):
    template_name = 'recyclers/aggregator_directory.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        company = self.get_company()
        lat, lon = float(company.latitude), float(company.longitude)
        entries = []
        for profile in AggregatorProfile.objects.filter(
            verification_status='approved',
        ).select_related('user'):
            entries.append({
                'profile': profile,
                'reference': aggregator_reference(profile),
            })
        ctx['entries'] = entries
        ctx['company'] = company
        return ctx


class ExportReportsCSVView(ApprovedCompanyMixin, View):
    def get(self, request, *args, **kwargs):
        company = self.get_company()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="{company.company_code or "recycler"}_report.csv"'
        )
        writer = csv.writer(response)
        writer.writerow([
            'Date',
            'Aggregator ref',
            'Host code',
            'Material',
            'Weight kg',
            'Gross KES',
        ])
        for row in company.traceability_records.all():
            writer.writerow([
                row.recorded_at.strftime('%Y-%m-%d %H:%M'),
                row.aggregator_reference,
                row.host_code,
                row.material_type,
                row.weight_kg,
                row.gross_amount,
            ])
        return response


class AdminCompanyListView(StaffRequiredMixin, TemplateView):
    template_name = 'recyclers/admin_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        status = self.request.GET.get('status', 'pending')
        qs = RecyclingCompany.objects.select_related('user').order_by('-submitted_at')
        if status != 'all':
            qs = qs.filter(status=status)
        ctx['companies'] = qs
        ctx['current_status'] = status
        return ctx


class AdminCompanyReviewView(StaffRequiredMixin, TemplateView):
    template_name = 'recyclers/admin_review.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['company'] = get_object_or_404(
            RecyclingCompany.objects.select_related('user', 'verified_by'),
            pk=self.kwargs['pk'],
        )
        ctx['reject_form'] = AdminRejectForm()
        ctx['price_rows'] = PriceTable.objects.filter(company=ctx['company'])
        return ctx


class AdminApproveCompanyView(StaffRequiredMixin, View):
    def post(self, request, pk):
        company = get_object_or_404(RecyclingCompany, pk=pk, status='pending')
        company.approve(request.user)
        send_welcome_email(company)
        messages.success(
            request,
            f'Approved {company.company_name}. Code: {company.company_code}',
        )
        return redirect('recycler_admin_list')


class AdminRejectCompanyView(StaffRequiredMixin, View):
    def post(self, request, pk):
        form = AdminRejectForm(request.POST)
        company = get_object_or_404(RecyclingCompany, pk=pk)
        if form.is_valid():
            company.reject(request.user, form.cleaned_data['rejection_reason'])
            messages.warning(request, f'Rejected {company.company_name}.')
            return redirect('recycler_admin_list')
        messages.error(request, 'Please provide a rejection reason.')
        return redirect('recycler_admin_review', pk=pk)