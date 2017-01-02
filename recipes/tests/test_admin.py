from .base import RecipeTestCase
from recipes.models import Kind


class AdminTest(RecipeTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_shows_ingredients(self):
        instance = self.create_ingredient(kind=Kind.Addition)

        response = self.client.get('/admin/recipes/ingredient/')

        self.assertContains(response, instance.name)
        self.assertContains(response, instance.price)
        self.assertContains(response, str(instance.kind))

    def test_shows_recipes(self):
        instance = self.create_recipe()

        response = self.client.get('/admin/recipes/recipe/')

        self.assertContains(response, instance.name)

    def test_lets_users_add_ingredient_to_new_recipe(self):
        ingredient = self.create_ingredient(name='Sand')

        response = self.client.get('/admin/recipes/recipe/add/')

        self.assertContains(response, ingredient.name)
