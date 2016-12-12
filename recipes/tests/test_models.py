from datetime import datetime
from decimal import Decimal

from django.test import TestCase

from recipes.models import Ingredient


class IngredientTest(TestCase):
    def test_creates_a_basic_ingredient(self):
        Ingredient.objects.create(
            name='Sand',
            price=Decimal('1.99'),
        )

        ingredient = Ingredient.objects.get(pk=1)

        self.assertEqual(ingredient.name, 'Sand')
        self.assertEqual(ingredient.price, Decimal('1.99'))
        self.assertIsInstance(ingredient.created, datetime)
        self.assertIsInstance(ingredient.updated, datetime)
