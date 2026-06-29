from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.template.loader import render_to_string

from accounts.geo import haversine_km

SOURCING_RADIUS_KM = getattr(settings, 'RECYCLER_SOURCING_RADIUS_KM', 75)


def generate_company_code():
    from .models import RecyclingCompany

    year = date.today().year
    prefix = f'RC-{year}-'
    existing = RecyclingCompany.objects.filter(
        company_code__startswith=prefix,
    ).count()
    return f'{prefix}{existing + 1:04d}'


def subscription_end_date(start_date):
    return start_date + timedelta(days=30)


def subscription_plan_amount(plan):
    return {'basic': 500, 'standard': 1000, 'premium': 1500}.get(plan, 0)


SUBSCRIPTION_FEATURES = {
    'basic': [
        'Supply pipeline visibility',
        'Traceability records (30 days)',
        'Monthly CSV export',
    ],
    'standard': [
        'Everything in Basic',
        'Analytics charts',
        'Aggregator directory',
        'Traceability (12 months)',
    ],
    'premium': [
        'Everything in Standard',
        'Priority support',
        'Unlimited CSV exports',
        'API access (coming soon)',
    ],
}


def get_material_price(material, company=None):
    """
    Price lookup for collection logging — reads active PriceTable rows.
    Import from recyclers in collection flows:

        from recyclers.services import get_material_price

    Falls back to platform average, then zero.
    """
    from .models import PriceTable

    if company is not None:
        row = PriceTable.objects.filter(
            company=company,
            material=material,
            is_active=True,
        ).first()
        if row:
            return row.price_per_kg

    avg = PriceTable.objects.filter(
        material=material,
        is_active=True,
    ).aggregate(avg=Avg('price_per_kg'))['avg']
    if avg is not None:
        return Decimal(str(avg)).quantize(Decimal('0.01'))
    return Decimal('0.00')


def aggregator_reference(aggregator_profile):
    return f'CA-{aggregator_profile.id:05d}'


def host_code(drop_off_center):
    return f'HOST-{drop_off_center.id:05d}'


def companies_near(lat, lon, radius_km=SOURCING_RADIUS_KM):
    from .models import RecyclingCompany

    results = []
    for company in RecyclingCompany.objects.filter(
        status='approved',
        subscription_active=True,
    ):
        dist = haversine_km(
            float(lat),
            float(lon),
            float(company.latitude),
            float(company.longitude),
        )
        if dist <= radius_km:
            results.append((dist, company))
    results.sort(key=lambda x: x[0])
    return results


def refresh_supply_pipeline(company, radius_km=SOURCING_RADIUS_KM):
    from aggregators.models import AggregatorPickupAssignment

    from .models import SupplyPipelineEntry

    SupplyPipelineEntry.objects.filter(company=company).delete()
    lat, lon = float(company.latitude), float(company.longitude)

    for assignment in AggregatorPickupAssignment.objects.filter(
        status__in=['assigned', 'in_progress'],
    ).select_related(
        'pickup_request__drop_off_center',
        'aggregator',
    ):
        center = assignment.pickup_request.drop_off_center
        if center.latitude is None or center.longitude is None:
            continue
        dist = haversine_km(
            lat,
            lon,
            float(center.latitude),
            float(center.longitude),
        )
        if dist <= radius_km:
            SupplyPipelineEntry.objects.create(
                company=company,
                assignment=assignment,
                distance_km=Decimal(str(round(dist, 2))),
                is_confirmed=True,
            )


def link_traceability_for_collection(collection_log):
    from aggregators.models import CollectionLog

    from .models import RecyclingCompany, TraceabilityRecord

    if not isinstance(collection_log, CollectionLog):
        return

    center = collection_log.drop_off_center
    if center.latitude is None or center.longitude is None:
        return

    lat, lon = float(center.latitude), float(center.longitude)
    for _dist, company in companies_near(lat, lon):
        TraceabilityRecord.objects.get_or_create(
            company=company,
            collection_log=collection_log,
            defaults={
                'aggregator_reference': aggregator_reference(collection_log.aggregator),
                'host_code': host_code(center),
                'material_type': collection_log.material_type,
                'weight_kg': collection_log.weight_kg,
                'gross_amount': collection_log.gross_amount,
                'recorded_at': collection_log.collected_at,
            },
        )


def send_registration_emails(company, admin_emails=None):
    context = {'company': company}
    company_body = render_to_string(
        'recyclers/emails/registration_confirmation.txt',
        context,
    )
    send_mail(
        subject='RecyCleanHub — Recycling company registration received',
        message=company_body,
        from_email=None,
        recipient_list=[company.company_email],
        fail_silently=True,
    )
    admin_body = render_to_string(
        'recyclers/emails/admin_new_registration.txt',
        context,
    )
    recipients = admin_emails or []
    if not recipients:
        from django.contrib.auth.models import User

        recipients = list(
            User.objects.filter(is_staff=True, is_active=True).values_list(
                'email',
                flat=True,
            ),
        )
    recipients = [e for e in recipients if e]
    if recipients:
        send_mail(
            subject=f'New recycling company pending: {company.company_name}',
            message=admin_body,
            from_email=None,
            recipient_list=recipients,
            fail_silently=True,
        )


def send_welcome_email(company):
    context = {
        'company': company,
        'plan_amount': subscription_plan_amount(company.subscription_plan),
    }
    body = render_to_string('recyclers/emails/welcome_approved.txt', context)
    send_mail(
        subject='Welcome to RecyCleanHub — Account approved',
        message=body,
        from_email=None,
        recipient_list=[company.company_email],
        fail_silently=True,
    )
