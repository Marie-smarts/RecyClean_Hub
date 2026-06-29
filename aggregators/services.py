from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings


def get_share_rates():
    platform = Decimal(str(getattr(settings, 'AGGREGATOR_PLATFORM_SHARE', '0.10')))
    aggregator = Decimal(str(getattr(settings, 'AGGREGATOR_COLLECTOR_SHARE', '0.60')))
    host = Decimal(str(getattr(settings, 'AGGREGATOR_HOST_SHARE', '0.30')))
    return platform, aggregator, host


def calculate_payment_split(gross_amount):
    """
    Split gross collection amount between platform, aggregator, and host.
    Returns (platform_amount, aggregator_amount, host_amount).
    """
    gross = Decimal(gross_amount).quantize(Decimal('0.01'))
    platform_rate, aggregator_rate, host_rate = get_share_rates()

    platform_amount = (gross * platform_rate).quantize(Decimal('0.01'), ROUND_HALF_UP)
    aggregator_amount = (gross * aggregator_rate).quantize(Decimal('0.01'), ROUND_HALF_UP)
    host_amount = (gross * host_rate).quantize(Decimal('0.01'), ROUND_HALF_UP)

    remainder = gross - platform_amount - aggregator_amount - host_amount
    if remainder:
        host_amount += remainder

    return platform_amount, aggregator_amount, host_amount
