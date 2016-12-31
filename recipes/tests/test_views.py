from decimal import Decimal

from .base import RecipeTestCase
from recipes.models import Kind, Ingredient


class LoggedInRecipeTestCase(RecipeTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)


class IngredientListTest(LoggedInRecipeTestCase):
    def test_loads_ingredients_page(self):
        ingredient = self.create_ingredient()

        response = self.client.get('/recipes/ingredients/')

        self.assertContains(response, ingredient.name)

    def test_doesnt_load_from_another_user(self):
        ingredient = self.create_ingredient(user=self.another_user)

        response = self.client.get('/recipes/ingredients/')

        self.assertNotContains(response, ingredient.name)


class IngredientDetailTest(LoggedInRecipeTestCase):
    def test_loads_ingredient_detail(self):
        ingredient = self.create_ingredient()

        response = self.client.get('/recipes/ingredients/1/')

        self.assertContains(response, ingredient.name)


class IngredientCreateTest(LoggedInRecipeTestCase):
    def test_loads_ingredient_add_page(self):
        response = self.client.get('/recipes/ingredient/add/')

        self.assertContains(response, 'form')

    def test_adds_ingredient(self):
        self.client.post('/recipes/ingredient/add/', {
            'name': 'Salt',
            'kind': Kind.BASE.value,
            'price': '12.34',
        })

        ingredient = Ingredient.objects.get(pk=1)

        self.assertEqual(ingredient.name, 'Salt')
        self.assertEqual(ingredient.kind, Kind.BASE)
        self.assertEqual(ingredient.price, Decimal('12.34'))
        self.assertEqual(ingredient.user, self.user)

    def test_cant_add_with_duplicate_name(self):
        self.create_ingredient(name='Salt')

        self.client.post('/recipes/ingredient/add/', {
            'name': 'Salt',
            'kind': Kind.BASE.value,
            'price': '12.34',
        })

        self.assertEqual(Ingredient.objects.count(), 1)


class IngredientUpdateTest(LoggedInRecipeTestCase):
    def test_loads_ingredient_edit_page(self):
        self.create_ingredient(name='Pepper')

        response = self.client.get('/recipes/ingredient/1/')

        self.assertContains(response, 'form')
        self.assertContains(response, 'Pepper')

    def test_cant_load_edit_if_not_owned(self):
        self.create_ingredient(name='Pepper', user=self.another_user)

        response = self.client.get('/recipes/ingredient/1/')

        self.assertEqual(response.status_code, 404)

    def test_updates_ingredient(self):
        self.create_ingredient(name='Salt')
        self.create_ingredient(name='Pepper')

        self.client.post('/recipes/ingredient/2/', {
            'name': 'Pepper 2',
            'kind': Kind.BASE.value,
            'price': '12.34',
        })

        ingredient = Ingredient.objects.get(pk=2)
        self.assertEqual(ingredient.name, 'Pepper 2')

    def test_cant_update_if_not_owned(self):
        self.create_ingredient(name='Pepper', user=self.another_user)

        response = self.client.post('/recipes/ingredient/1/', {
            'name': 'Pepper 2',
            'kind': Kind.BASE.value,
            'price': '12.34',
        })

        self.assertEqual(response.status_code, 404)


class RecipeViewsTest(LoggedInRecipeTestCase):
    def test_loads_recipes_page(self):
        recipe = self.create_recipe()

        response = self.client.get('/recipes/recipes/')

        self.assertContains(response, recipe.name)

    def test_doesnt_load_from_another_user(self):
        recipe = self.create_recipe(user=self.another_user)

        response = self.client.get('/recipes/recipes/')

        self.assertNotContains(response, recipe.name)
