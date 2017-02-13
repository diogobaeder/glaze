from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.db import IntegrityError
from model_mommy import mommy

from .base import RecipeTestCase
from recipes.models import Kind, Ingredient, Recipe, WeightUnit


class IngredientTest(RecipeTestCase):
    def test_creates_a_basic_ingredient(self):
        Ingredient.objects.create(
            user=self.user,
            name='Sand',
            price=Decimal('1.99'),
            kind=Kind.Addition,
            weight_unit=WeightUnit.Kg,
        )

        ingredient = Ingredient.objects.get(pk=1)

        self.assertEqual(ingredient.user, self.user)
        self.assertEqual(str(ingredient), 'Sand')
        self.assertEqual(ingredient.name, 'Sand')
        self.assertEqual(ingredient.price, Decimal('1.99'))
        self.assertEqual(ingredient.kind, Kind.Addition)
        self.assertIsInstance(ingredient.created, datetime)
        self.assertIsInstance(ingredient.updated, datetime)
        self.assertEqual(ingredient.weight_unit, WeightUnit.Kg)

    def test_cannot_create_ingredients_with_same_name(self):
        Ingredient.objects.create(
            user=self.user,
            name='Sand',
            price=Decimal('1.99'),
            kind=Kind.Addition,
            weight_unit=WeightUnit.Kg,
        )

        with self.assertRaises(IntegrityError):
            Ingredient.objects.create(
                user=self.user,
                name='Sand',
                price=Decimal('1.99'),
            )

    def test_can_create_ingredients_with_same_name_but_different_users(self):
        Ingredient.objects.create(
            user=self.user,
            name='Sand',
            price=Decimal('1.99'),
            kind=Kind.Addition,
            weight_unit=WeightUnit.Kg,
        )
        Ingredient.objects.create(
            user=mommy.make(User),
            name='Sand',
            price=Decimal('1.99'),
            kind=Kind.Addition,
            weight_unit=WeightUnit.Kg,
        )


class RecipeTest(RecipeTestCase):
    def test_creates_a_basic_recipe(self):
        Recipe.objects.create(
            user=self.user,
            name='Interesting Yellow'
        )

        recipe = Recipe.objects.get(pk=1)

        self.assertEqual(recipe.name, 'Interesting Yellow')
        self.assertEqual(recipe.user, self.user)
        self.assertIsInstance(recipe.created, datetime)
        self.assertIsInstance(recipe.updated, datetime)

    def test_can_have_description_field(self):
        Recipe.objects.create(
            user=self.user,
            name='Interesting Yellow',
            description='Some description',
        )

        recipe = Recipe.objects.get(pk=1)

        self.assertEqual(recipe.description, 'Some description')

    def test_can_have_image_field(self):
        with self.fixture('django.gif') as f:
            Recipe.objects.create(
                user=self.user,
                name='Interesting Yellow',
                image=ImageFile(f),
            )

        recipe = Recipe.objects.get(pk=1)

        self.assertIn('django', recipe.image.name)
        self.assertIn('gif', recipe.image.name)

    def test_can_load_image(self):
        with self.fixture('django.gif') as f:
            Recipe.objects.create(
                user=self.user,
                name='Interesting Yellow',
                image=ImageFile(f, 'fixtures/django.gif'),
            )

        recipe = Recipe.objects.get(pk=1)

        response = self.client.get(recipe.image.url)

        self.assertEqual(response.status_code, 200)

    def test_contains_ingredients_in_certain_percentages(self):
        ingredient1 = self.create_ingredient(
            price=Decimal('1.23'), weight_unit=WeightUnit.g)
        ingredient2 = self.create_ingredient(
            price=Decimal('2.34'), weight_unit=WeightUnit.Kg)
        recipe = Recipe.objects.create(
            user=self.user,
            name='Interesting Yellow'
        )

        recipe.add_part(ingredient1, percentage=Decimal('20'))
        recipe.add_part(ingredient2, percentage=Decimal('30'))

        parts = recipe.parts
        self.assertEqual(parts[0].ingredient, ingredient1)
        self.assertEqual(parts[1].ingredient, ingredient2)
        self.assertEqual(parts[0].percentage, Decimal('20'))
        self.assertEqual(parts[1].percentage, Decimal('30'))
        self.assertEqual(
            parts[0].relative_price,
            Decimal('1.23') * Decimal('1000') * Decimal('20') / Decimal('100'))
        self.assertEqual(
            parts[1].relative_price,
            Decimal('2.34') * Decimal('1') * Decimal('30') / Decimal('100'))

    def test_calculates_price_based_on_ingredients(self):
        ingredient1 = self.create_ingredient(
            price=Decimal('1.23'), weight_unit=WeightUnit.g)
        ingredient2 = self.create_ingredient(
            price=Decimal('2.34'), weight_unit=WeightUnit.Kg)
        recipe = Recipe.objects.create(
            user=self.user,
            name='Interesting Yellow'
        )

        recipe.add_part(ingredient1, percentage=Decimal('20'))
        recipe.add_part(ingredient2, percentage=Decimal('30'))

        self.assertEqual(recipe.price, (
            Decimal('1.23') * Decimal('1000') * Decimal('20') +
            Decimal('2.34') * Decimal('1') * Decimal('30')
        ) / (Decimal('20') + Decimal('30')))

    def test_uses_correct_multiplication_for_price(self):
        """Just a sanity check test."""
        ingredient1 = self.create_ingredient(
            price=Decimal('0.05'), weight_unit=WeightUnit.g)
        ingredient2 = self.create_ingredient(
            price=Decimal('50.00'), weight_unit=WeightUnit.Kg)
        recipe = Recipe.objects.create(
            user=self.user,
            name='Interesting Yellow'
        )

        recipe.add_part(ingredient1, percentage=Decimal('50'))
        recipe.add_part(ingredient2, percentage=Decimal('50'))

        self.assertEqual(recipe.price, Decimal('50.00'))

    def test_calculates_price_for_no_parts(self):
        recipe = Recipe.objects.create(
            user=self.user,
            name='Null Recipe',
        )

        self.assertEqual(recipe.price, Decimal('0'))

    def test_copies_a_recipe(self):
        ingredient1 = self.create_ingredient(
            price=Decimal('1.23'), weight_unit=WeightUnit.g)
        ingredient2 = self.create_ingredient(
            price=Decimal('2.34'), weight_unit=WeightUnit.Kg)
        recipe1 = Recipe.objects.create(
            user=self.user,
            name='Interesting Yellow'
        )
        recipe1.add_part(ingredient1, percentage=Decimal('20'))
        recipe1.add_part(ingredient2, percentage=Decimal('30'))
        id1 = recipe1.pk
        price1 = recipe1.price
        name1 = recipe1.name

        recipe2 = recipe1.clone()
        recipe2 = Recipe.objects.get(pk=recipe2.pk)

        self.assertNotEqual(recipe2.pk, id1)
        self.assertEqual(recipe2.price, price1)
        self.assertEqual(recipe2.price, recipe1.price)
        self.assertEqual(recipe2.name, '{} (Copy of {})'.format(name1, id1))


class KindTest(RecipeTestCase):
    def test_converts_to_pretty_name(self):
        self.assertEqual(str(Kind.Base), 'Base')
        self.assertEqual(str(Kind.Addition), 'Addition')


class WeightUnitTest(RecipeTestCase):
    def test_gets_weighted_in_for_equal_units(self):
        self.assertEqual(
            WeightUnit.Kg.weighted_in(WeightUnit.Kg), Decimal('1'))
        self.assertEqual(
            WeightUnit.g.weighted_in(WeightUnit.g), Decimal('1'))

    def test_gets_kg_weighted_in_g(self):
        self.assertEqual(
            WeightUnit.Kg.weighted_in(WeightUnit.g), Decimal('1000'))

    def test_gets_g_weighted_in_kg(self):
        self.assertEqual(
            WeightUnit.g.weighted_in(WeightUnit.Kg), Decimal('0.001'))
