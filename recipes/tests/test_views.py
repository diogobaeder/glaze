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

    def test_doesnt_load_from_another_user(self):
        ingredient = self.create_ingredient(user=self.another_user)

        self.client.force_login(self.user)
        response = self.client.get('/recipes/ingredients/')

        self.assertNotContains(response, ingredient.name)


class RecipeViewsTest(RecipeTestCase):
    def test_loads_recipes_page(self):
        recipe = self.create_recipe()

        self.client.force_login(self.user)
        response = self.client.get('/recipes/recipes/')

        self.assertContains(response, recipe.name)

    def test_doesnt_load_from_another_user(self):
        recipe = self.create_recipe(user=self.another_user)

        self.client.force_login(self.user)
        response = self.client.get('/recipes/recipes/')

        self.assertNotContains(response, recipe.name)
