from model_mommy import mommy

from glaze.tests.base import GlazeTestCase
from recipes.models import Ingredient, Recipe


class RecipeTestCase(GlazeTestCase):
    def create_ingredient(self, **kwargs) -> Ingredient:
        kwargs.setdefault('user', self.user)
        return mommy.make(Ingredient, **kwargs)

    def create_recipe(self, **kwargs) -> Recipe:
        kwargs.setdefault('user', self.user)
        return mommy.make(Recipe, **kwargs)
