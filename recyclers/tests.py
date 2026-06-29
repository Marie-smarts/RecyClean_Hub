from decimal import Decimal

from django.test import TestCase

from .services import get_material_price


class PriceTableServiceTests(TestCase):
    def test_get_material_price_default_zero(self):
        self.assertEqual(get_material_price('plastic'), Decimal('0.00'))
