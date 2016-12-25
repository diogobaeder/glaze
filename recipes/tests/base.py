from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy

from recipes.models import Ingredient, Recipe


class BaseRecipeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            'john', 'john.doe@example.com', 'test123!')

    def create_ingredient(self, **kwargs):
        return mommy.make(Ingredient, user=self.user, **kwargs)

    def create_recipe(self, **kwargs):
        return mommy.make(Recipe, user=self.user, **kwargs)
