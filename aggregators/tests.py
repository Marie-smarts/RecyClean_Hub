from decimal import Decimal

from django.test import TestCase

from .services import calculate_payment_split


class PaymentSplitTests(TestCase):
    def test_split_sums_to_gross(self):
        gross = Decimal('1000.00')
        platform, aggregator, host = calculate_payment_split(gross)
        self.assertEqual(platform + aggregator + host, gross)
