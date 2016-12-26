from .base import RecipeTestCase


class AccessTest(RecipeTestCase):
    def test_cannot_load_ingredients_if_not_logged_in(self):
        response = self.client.get('/recipes/ingredients/')

        self.assertRedirects(
            response, '/accounts/login/?next=/recipes/ingredients/')


class IngredientViewsTest(RecipeTestCase):
    def test_loads_ingredients_page(self):
        ingredient = self.create_ingredient()

        self.client.force_login(self.user)
        response = self.client.get('/recipes/ingredients/')

        self.assertContains(response, ingredient.name)
