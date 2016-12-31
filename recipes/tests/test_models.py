from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.db import IntegrityError
from model_mommy import mommy

from .base import RecipeTestCase
from recipes.models import Kind, Ingredient, Recipe


class IngredientTest(RecipeTestCase):
    def test_creates_a_basic_ingredient(self):
        Ingredient.objects.create(
            user=self.user,
            name='Sand',
            price=Decimal('1.99'),
            kind=Kind.ADDITION,
        )

        ingredient = Ingredient.objects.get(pk=1)

        self.assertEqual(ingredient.user, self.user)
        self.assertEqual(str(ingredient), 'Sand')
        self.assertEqual(ingredient.name, 'Sand')
        self.assertEqual(ingredient.price, Decimal('1.99'))
        self.assertEqual(ingredient.kind, Kind.ADDITION)
        self.assertIsInstance(ingredient.created, datetime)
        self.assertIsInstance(ingredient.updated, datetime)

    def test_cannot_create_ingredients_with_same_name(self):
        Ingredient.objects.create(
            user=self.user,
            name='Sand',
            price=Decimal('1.99'),
            kind=Kind.ADDITION,
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
            kind=Kind.ADDITION,
        )
        Ingredient.objects.create(
            user=mommy.make(User),
            name='Sand',
            price=Decimal('1.99'),
            kind=Kind.ADDITION,
        )

    def test_gets_kind_name(self):
        instance = self.create_ingredient(kind=Kind.ADDITION)

        self.assertEqual(instance.kind_name, 'Addition')


class RecipeTest(RecipeTestCase):
    def some_ingredient(self):
        return mommy.make(Ingredient, user=self.user)

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

    def test_contains_ingredients_in_certain_quantities(self):
        ingredient1 = self.some_ingredient()
        ingredient2 = self.some_ingredient()
        recipe = Recipe.objects.create(
            user=self.user,
            name='Interesting Yellow'
        )

        recipe.add_part(ingredient1, quantity=Decimal('0.2'))
        recipe.add_part(ingredient2, quantity=Decimal('0.3'))

        parts = recipe.parts
        self.assertEqual(parts[0].ingredient, ingredient1)
        self.assertEqual(parts[1].ingredient, ingredient2)
        self.assertEqual(parts[0].quantity, Decimal('0.2'))
        self.assertEqual(parts[1].quantity, Decimal('0.3'))

    def test_calculates_price_based_on_ingredients(self):
        ingredient1 = self.some_ingredient()
        ingredient2 = self.some_ingredient()
        recipe = Recipe.objects.create(
            user=self.user,
            name='Interesting Yellow'
        )

        recipe.add_part(ingredient1, quantity=Decimal('0.2'))
        recipe.add_part(ingredient2, quantity=Decimal('0.3'))

        self.assertEqual(recipe.price, (
            ingredient1.price * Decimal('0.2') +
            ingredient2.price * Decimal('0.3')
        ))
