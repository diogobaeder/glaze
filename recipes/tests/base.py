from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy

from recipes.models import Ingredient, Recipe


class RecipeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            'john', 'john.doe@example.com', 'test123!')
        self.another_user = User.objects.create_user(
            'alice', 'alice@example.com', 'test123!')

    def create_ingredient(self, **kwargs) -> Ingredient:
        kwargs.setdefault('user', self.user)
        return mommy.make(Ingredient, **kwargs)

    def create_recipe(self, **kwargs) -> Recipe:
        kwargs.setdefault('user', self.user)
        return mommy.make(Recipe, **kwargs)
