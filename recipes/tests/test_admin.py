from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy

from .base import BaseRecipeTestCase
from recipes.models import Kind, Ingredient, Recipe


class AdminTest(BaseRecipeTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_shows_ingredients(self):
        instance = self.create_ingredient(kind=Kind.ADDITION)

        response = self.client.get('/admin/recipes/ingredient/')

        self.assertContains(response, instance.name)
        self.assertContains(response, instance.price)
        self.assertContains(response, instance.kind_name)

    def test_shows_recipes(self):
        instance = self.create_recipe()

        response = self.client.get('/admin/recipes/recipe/')

        self.assertContains(response, instance.name)

    def test_lets_users_add_ingredient_to_new_recipe(self):
        ingredient = self.create_ingredient(name='Sand')

        response = self.client.get('/admin/recipes/recipe/add/')

        self.assertContains(response, ingredient.name)
