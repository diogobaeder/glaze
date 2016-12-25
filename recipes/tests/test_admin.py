from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy

from .base import BaseRecipeTestCase
from recipes.models import Ingredient, Recipe


class AdminTest(BaseRecipeTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_shows_ingredients(self):
        instance = self.create_ingredient()

        response = self.client.get('/admin/recipes/ingredient/')

        self.assertContains(response, instance.name)

    def test_shows_recipes(self):
        instance = self.create_recipe()

        response = self.client.get('/admin/recipes/recipe/')

        self.assertContains(response, instance.name)
